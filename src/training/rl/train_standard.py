import os
import math
import argparse
import numpy as np
import pygame
from config.constants import GRID_WIDTH, GRID_LENGTH
from core.game_logic import GameLogic
from core.utils.core_utils import game_over, rearrange, remove_redundant, _get_remove_values
from agents.rl.standard import NoTeacherAgent
from ui.game.game_ui import GameUI
from training.debug.no_teacher_visualizer import NoTeacherVisualizer


def _compute_reward(score_delta: float, merge_count: float,
                    matrix_before: list, merged: bool) -> float:
    total_cells = GRID_WIDTH * GRID_LENGTH
    empty_cells = sum(1 for row in matrix_before for v in row if v == 0)
    survival_bonus = empty_cells / total_cells
    if not merged:
        return -10.0
    score_term = math.log2(score_delta + 1) * 0.5 if score_delta > 0 else 0.0
    merge_bonus = merge_count / (merge_count + 2.0)
    return score_term * 0.5 + survival_bonus * 0.3 + merge_bonus * 0.2


class NoTeacherTrainer:
    def __init__(
        self,
        episodes: int = 200,
        save_every: int = 50,
        output_path: str = "data/rl_no_teacher_agent.json",
        fps: int = 120,
        learning_rate: float = 0.1,
        headless: bool = False,
    ):
        self.episodes = episodes
        self.save_every = save_every
        self.output_path = output_path
        self.fps = fps
        self.headless = headless
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.agent = NoTeacherAgent(learning_rate=learning_rate)
        self.game = GameLogic()
        self.history = []
        self.weight_volatility = 0.0
        self.epsilon_start = 1.0
        self.epsilon_end = 0.01
        self.epsilon_decay = 0.99
        self.epsilon = self.epsilon_start
        if not self.headless:
            self.ui = GameUI(self.game)
            self.visualizer = NoTeacherVisualizer(self.agent.feature_names)
            current_w, current_h = self.ui.screen.get_size()
            self.ui.screen = pygame.display.set_mode(
                (current_w + self.visualizer.width, current_h)
            )
            self.game_width = current_w
        else:
            self.ui = None
            self.visualizer = None
            self.game_width = 0

    def reset_episode(self):
        if self.headless:
            self.game = GameLogic()
            self.next_value = self.game.get_random_value()
        else:
            self.ui.reset_game()
            self.ui.next_value = self.game.get_random_value()

    def run_episode_headless(self, episode_idx: int) -> float:
        episode_reward = 0.0
        total_volatility = []
        while True:
            matrix = self.game.get_matrix()
            if game_over(matrix, self.next_value):
                break
            action = self.agent.select_action(matrix, self.next_value, self.epsilon)
            feature_vectors = self.agent._get_action_space_features(matrix, self.next_value)
            state_features = feature_vectors[action]
            if state_features is None:
                break
            merged, count = self.game.add_to_column(self.next_value, action)
            reward = _compute_reward(float(count), float(count), matrix, bool(merged))
            episode_reward += reward
            new_matrix = self.game.get_matrix()
            new_matrix = rearrange(new_matrix)
            max_val = max(max(r) for r in new_matrix) if new_matrix else 0
            remove_values = _get_remove_values(max_val)
            try:
                _, new_matrix = remove_redundant(matrix=new_matrix, remove_values=remove_values)
            except Exception:
                pass
            while True:
                merged_m, _ = self.game.merge_column()
                if not merged_m:
                    break
                new_matrix = rearrange(new_matrix)
            self.game.set_matrix(new_matrix)
            next_val = self.game.get_random_value()
            vol = self.agent.update_q_learning(
                state_features, reward, self.game.get_matrix(), next_val, not merged
            )
            total_volatility.append(vol)
            self.next_value = next_val
        if total_volatility:
            self.weight_volatility = float(np.mean(total_volatility))
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        return episode_reward

    def run_episode(self, episode_idx: int) -> float:
        episode_reward = 0.0
        total_volatility = []
        while True:
            matrix = self.game.get_matrix()
            if game_over(matrix, self.ui.next_value):
                self.ui.draw_game_over()
                break
            self.ui.handle_events()
            if not self.ui.game_is_over and self.ui.input_column is None:
                action = self.agent.select_action(matrix, self.ui.next_value, self.epsilon)
                feature_vectors = self.agent._get_action_space_features(
                    matrix, self.ui.next_value
                )
                state_features = feature_vectors[action]
                self.ui.input_column = action
                self.ui.trigger_drop_animation(action, self.ui.next_value)
            if not self.ui.game_is_over and self.ui.input_column is not None and state_features is not None:
                old_matrix = [row[:] for row in self.game.get_matrix()]
                merged, count = self.game.add_to_column(self.ui.next_value, self.ui.input_column)
                reward = _compute_reward(float(count), float(count), old_matrix, bool(merged))
                episode_reward += reward
                if not merged:
                    self.game.merge_column(self.ui.input_column)
                    self.ui.drop_animations = []
                else:
                    new_matrix = self.game.get_matrix()
                    self.ui.detect_and_trigger_animations(old_matrix, new_matrix, self.ui.input_column)
                    next_val = self.game.get_random_value()
                    vol = self.agent.update_q_learning(
                        state_features, reward, self.game.get_matrix(), next_val, False
                    )
                    total_volatility.append(vol)
                    self.ui.next_value = next_val
                    self.ui.input_column = None
            current_matrix = self.game.get_matrix()
            current_matrix = rearrange(current_matrix)
            max_val = max(max(r) for r in current_matrix) if current_matrix else 0
            remove_values = _get_remove_values(max_val)
            try:
                _, current_matrix = remove_redundant(matrix=current_matrix, remove_values=remove_values)
            except Exception:
                pass
            while True:
                merged_m, _ = self.game.merge_column()
                if not merged_m:
                    break
                current_matrix = rearrange(current_matrix)
            self.game.set_matrix(current_matrix)
            self.ui.draw_matrix()
            self.visualizer.draw(
                self.ui.screen,
                self.agent.get_weights(),
                self.history,
                self.epsilon,
                self.weight_volatility,
                self.game_width,
            )
            pygame.display.flip()
            self.ui.clock.tick(self.fps)
        if total_volatility:
            self.weight_volatility = float(np.mean(total_volatility))
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        return episode_reward

    def run(self):
        for ep in range(self.episodes):
            self.reset_episode()
            if self.headless:
                reward = self.run_episode_headless(ep)
            else:
                reward = self.run_episode(ep)
            self.history.append(reward)
            if (ep + 1) % self.save_every == 0:
                self.agent.save(self.output_path)
            print(
                f"Episode {ep + 1}/{self.episodes}  "
                f"Reward: {reward:.3f}  "
                f"ε: {self.epsilon:.4f}  "
                f"Volatility: {self.weight_volatility:.5f}"
            )
        self.agent.save(self.output_path)


def run_no_teacher_training():
    parser = argparse.ArgumentParser(
        description="No-Teacher RL Training"
    )
    parser.add_argument("--episodes", type=int, default=200, help="Number of episodes")
    parser.add_argument("--fps", type=int, default=120, help="Training speed (visual mode)")
    parser.add_argument("--lr", type=float, default=0.1, help="Learning rate")
    parser.add_argument(
        "--headless", action="store_true",
        help="Run without pygame display"
    )
    args = parser.parse_args()
    trainer = NoTeacherTrainer(
        episodes=args.episodes,
        fps=args.fps,
        learning_rate=args.lr,
        headless=args.headless,
    )
    trainer.run()


if __name__ == "__main__":
    run_no_teacher_training()

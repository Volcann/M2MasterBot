import os
import math
import argparse
import numpy as np
import pygame
from config.constants import GRID_WIDTH, GRID_LENGTH
from core.game_logic import GameLogic
from core.utils.core_utils import game_over, rearrange, remove_redundant, _get_remove_values
from agents.rl.teacher import RLAgent
from ui.game.game_ui import GameUI
from training.debug.teacher_enhanced_visualizer import TeacherEnhancedVisualizer


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


class UITrainer:
    def __init__(
        self,
        loop_count: int = 50,
        save_every: int = 50,
        output_path: str = "data/rl_agent.json",
        fps: int = 60,
        headless: bool = False,
    ):
        self.loop_count = loop_count
        self.save_every = save_every
        self.output_path = output_path
        self.fps = fps
        self.headless = headless
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.agent = RLAgent()
        self.game = GameLogic()
        self.history = []
        self.alignment_score = 0.0
        if not self.headless:
            self.ui = GameUI(self.game)
            self.visualizer = TeacherEnhancedVisualizer(self.agent.feature_names)
            current_w, current_h = self.ui.screen.get_size()
            self.ui.screen = pygame.display.set_mode(
                (current_w + self.visualizer.width, current_h)
            )
            self.game_width = current_w
        else:
            self.ui = None
            self.visualizer = None
            self.game_width = 0
        self.agent.load(output_path)

    def reset_episode(self):
        if self.headless:
            self.game = GameLogic()
            self.next_value = self.game.get_random_value()
        else:
            self.ui.reset_game()
            self.ui.next_value = self.game.get_random_value()

    def run_episode_headless(self) -> float:
        episode_score = 0.0
        while True:
            matrix = self.game.get_matrix()
            if game_over(matrix, self.next_value):
                break
            chosen_action, state_features, teacher_action, agent_action = (
                self.agent.select_action_with_teacher(matrix, self.next_value)
            )
            self.alignment_score = 1.0 if chosen_action == teacher_action else 0.0
            old_matrix = [row[:] for row in matrix]
            merged, count = self.game.add_to_column(self.next_value, chosen_action)
            reward = _compute_reward(float(count), float(count), old_matrix, bool(merged))
            episode_score += max(reward, 0.0)
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
            self.agent.update_q_learning(
                state_features, reward, self.game.get_matrix(), next_val, not merged
            )
            self.next_value = next_val
        return episode_score

    def run_episode(self) -> float:
        episode_score = 0.0
        state_features = np.zeros(len(self.agent.feature_names))
        while True:
            matrix = self.game.get_matrix()
            if game_over(matrix, self.ui.next_value):
                self.ui.draw_game_over()
                break
            self.ui.handle_events()
            if not self.ui.game_is_over and self.ui.input_column is None:
                chosen_action, state_features, teacher_action, agent_action = (
                    self.agent.select_action_with_teacher(matrix, self.ui.next_value)
                )
                self.alignment_score = 1.0 if agent_action == teacher_action else 0.0
                self.ui.input_column = chosen_action
                self.ui.trigger_drop_animation(chosen_action, self.ui.next_value)
            show_message = False
            if not self.ui.game_is_over and self.ui.input_column is not None:
                old_matrix = [row[:] for row in self.game.get_matrix()]
                merged, count = self.game.add_to_column(
                    self.ui.next_value, self.ui.input_column
                )
                reward = _compute_reward(float(count), float(count), old_matrix, bool(merged))
                if not merged:
                    show_message = True
                    self.game.merge_column(self.ui.input_column)
                    self.ui.drop_animations = []
                else:
                    new_matrix = self.game.get_matrix()
                    self.ui.detect_and_trigger_animations(
                        old_matrix, new_matrix, self.ui.input_column
                    )
                    episode_score += float(count)
                    next_val = self.game.get_random_value()
                    self.agent.update_q_learning(
                        state_features, reward, self.game.get_matrix(), next_val, False
                    )
                    self.ui.next_value = next_val
                    self.ui.input_column = None
            if show_message and not self.ui.game_is_over:
                self.ui.show_temp_message("Column is full!")
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
                self.alignment_score,
                self.game_width,
                teacher_lambda=self.agent.teacher_lambda,
            )
            pygame.display.flip()
            self.ui.clock.tick(self.fps)
        return episode_score

    def run(self):
        episode = 0
        last_save = 0
        while episode < self.loop_count:
            self.reset_episode()
            if self.headless:
                reward = self.run_episode_headless()
            else:
                reward = self.run_episode()
            self.history.append(reward)
            episode += 1
            last_save += 1
            if last_save >= self.save_every:
                self.agent.save(self.output_path)
                last_save = 0
            print(
                f"Episode {episode}/{self.loop_count}  "
                f"Score: {reward:.1f}  "
                f"λ: {self.agent.teacher_lambda:.4f}  "
                f"Alignment: {self.alignment_score:.2f}"
            )
        self.agent.save(self.output_path)


def run_ui_training():
    parser = argparse.ArgumentParser(description="M2MasterBot Teacher RL Training")
    parser.add_argument("--episodes", type=int, default=100, help="Number of episodes")
    parser.add_argument("--save-every", type=int, default=50, help="Save interval")
    parser.add_argument("--output-path", type=str, default="data/rl_agent.json")
    parser.add_argument("--fps", type=int, default=120, help="Training speed (FPS)")
    parser.add_argument(
        "--headless", action="store_true",
        help="Skip pygame rendering"
    )
    args = parser.parse_args()
    trainer = UITrainer(
        loop_count=args.episodes,
        save_every=args.save_every,
        output_path=args.output_path,
        fps=args.fps,
        headless=args.headless,
    )
    trainer.run()


if __name__ == "__main__":
    run_ui_training()

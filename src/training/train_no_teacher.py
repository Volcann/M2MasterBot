import os
import argparse
import pygame
import numpy as np
from typing import List

from core.game_logic import GameLogic
from core.utils.utils import game_over, rearrange, remove_redundant, _get_remove_values
from rl_no_teacher.agent import NoTeacherAgent
from ui.game.game_ui import GameUI
from training.debug.no_teacher_visualizer import NoTeacherVisualizer


class NoTeacherTrainer:
    def __init__(
        self,
        episodes: int = 200,
        save_every: int = 50,
        output_path: str = "data/rl_no_teacher_agent.json",
        fps: int = 120,
        learning_rate: float = 0.1,
    ):
        self.episodes = episodes
        self.save_every = save_every
        self.output_path = output_path
        self.fps = fps
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self.agent = NoTeacherAgent(learning_rate=learning_rate)
        self.game = GameLogic()
        self.ui = GameUI(self.game)

        self.visualizer = NoTeacherVisualizer(self.agent.feature_names)
        self.history = []
        self.weight_volatility = 0.0

        current_w, current_h = self.ui.screen.get_size()
        self.ui.screen = pygame.display.set_mode(
            (current_w + self.visualizer.width, current_h)
        )
        self.game_width = current_w

        # Exploration params
        self.epsilon_start = 1.0
        self.epsilon_end = 0.01
        self.epsilon_decay = 0.99
        self.epsilon = self.epsilon_start

    def reset_episode(self):
        self.ui.reset_game()
        self.ui.next_value = self.game.get_random_value()

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
                # Epsilon-greedy selection
                action = self.agent.select_action(matrix, self.ui.next_value, self.epsilon)
                
                # Get current state features for the chosen action
                feature_vectors = self.agent._get_action_space_features(matrix, self.ui.next_value)
                state_features = feature_vectors[action]

                self.ui.input_column = action
                self.ui.trigger_drop_animation(action, self.ui.next_value)
                
                # SIMULATE THE MOVE and GET REWARD
                old_matrix = [row[:] for row in self.game.get_matrix()]
                merged, count = self.game.add_to_column(self.ui.next_value, action)
                
                # --- Sparse Reward Logic ---
                # Only reward merges >= 128
                reward = 0.0
                if merged and self.ui.next_value >= 128:
                    reward = 1.0
                
                # Post-move cleanup (standard game logic)
                new_matrix = self.game.get_matrix()
                self.ui.detect_and_trigger_animations(old_matrix, new_matrix, action)
                episode_reward += reward
                
                # Update Q-values
                next_val = self.game.get_random_value()
                vol = self.agent.update_q_learning(
                    state_features, 
                    reward, 
                    new_matrix, 
                    next_val, 
                    False
                )
                total_volatility.append(vol)

                self.ui.next_value = next_val
                self.ui.input_column = None

            # Handle game cleanup and UI
            current_matrix = self.game.get_matrix()
            current_matrix = rearrange(current_matrix)
            max_val = max(max(r) for r in current_matrix) if current_matrix else 0
            remove_values = _get_remove_values(max_val)
            try:
                _, current_matrix = remove_redundant(
                    matrix=current_matrix, 
                    remove_values=remove_values
                )
            except Exception:
                pass

            while True:
                merged, _ = self.game.merge_column()
                if not merged:
                    break
                current_matrix = rearrange(current_matrix)

            self.game.set_matrix(current_matrix)
            self.ui.draw_matrix()
            
            # Draw visualizer with extra metrics
            self.visualizer.draw(
                self.ui.screen, 
                self.agent.get_weights(), 
                self.history, 
                self.epsilon,
                self.weight_volatility,
                self.game_width
            )

            pygame.display.flip()
            self.ui.clock.tick(self.fps)

        # Update average volatility for this episode
        if total_volatility:
            self.weight_volatility = float(np.mean(total_volatility))
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        
        return episode_reward

    def run(self):
        for ep in range(self.episodes):
            self.reset_episode()
            reward = self.run_episode(ep)
            self.history.append(reward)

            if (ep + 1) % self.save_every == 0:
                self.agent.save(self.output_path)

            print(f"Episode {ep+1}/{self.episodes} Sparse Reward: {reward} Epsilon: {self.epsilon:.3f}")

        self.agent.save(self.output_path)


def run_no_teacher_training():
    parser = argparse.ArgumentParser(description="No-Teacher RL Training (Visualize Failure Cycle)")
    parser.add_argument("--episodes", type=int, default=200, help="Number of episodes")
    parser.add_argument("--fps", type=int, default=120, help="Training speed")
    parser.add_argument("--lr", type=float, default=0.1, help="Learning rate (high to trigger collapse)")
    
    args = parser.parse_args()

    trainer = NoTeacherTrainer(
        episodes=args.episodes,
        fps=args.fps,
        learning_rate=args.lr
    )
    trainer.run()


if __name__ == "__main__":
    run_no_teacher_training()

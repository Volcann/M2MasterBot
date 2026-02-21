import os
import argparse
import pygame
from typing import List

from core.game_logic import GameLogic
from core.utils.utils import game_over, rearrange, remove_redundant, _get_remove_values
from rl_agent_with_teacher.agent import RLAgent
from ui.game.game_ui import GameUI
from training.debug.visualizer import RLVisualizer


class UITrainer:
    def __init__(
        self,
        loop_count: int = 50,
        save_every: int = 50,
        output_path: str = "data/rl_agent.json",
        fps: int = 60,
    ):
        self.loop_count = loop_count
        self.save_every = save_every
        self.output_path = output_path
        self.fps = fps
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self.agent = RLAgent()
        self.game = GameLogic()
        self.ui = GameUI(self.game)

        self.visualizer = RLVisualizer(self.agent.feature_names)
        self.history = []

        current_w, current_h = self.ui.screen.get_size()
        self.ui.screen = pygame.display.set_mode(
            (current_w + self.visualizer.width, current_h)
        )
        self.game_width = current_w

        self.agent.load(output_path)

    def reset_episode(self):
        self.ui.reset_game()
        self.ui.next_value = self.game.get_random_value()

    def run_episode(self) -> float:
        episode_score = 0.0
        while True:
            matrix = self.game.get_matrix()
            if game_over(matrix, self.ui.next_value):
                self.ui.draw_game_over()
                break

            self.ui.handle_events()

            if not self.ui.game_is_over and self.ui.input_column is None:
                action = self.agent.train_from_heuristic(
                    matrix, 
                    self.ui.next_value
                )

                self.ui.input_column = action
                self.ui.trigger_drop_animation(action, self.ui.next_value)

            show_message = False

            if not self.ui.game_is_over and self.ui.input_column is not None:
                old_matrix = [row[:] for row in self.game.get_matrix()]
                merged, count = self.game.add_to_column(
                    self.ui.next_value, 
                    self.ui.input_column
                )

                if not merged:
                    show_message = True
                    self.game.merge_column(self.ui.input_column)
                    self.ui.drop_animations = []
                else:
                    new_matrix = self.game.get_matrix()
                    self.ui.detect_and_trigger_animations(
                        old_matrix, 
                        new_matrix, 
                        self.ui.input_column
                    )
                    episode_score += float(count)
                    self.ui.next_value = self.game.get_random_value()
                    self.ui.input_column = None

            if show_message and not self.ui.game_is_over:
                self.ui.show_temp_message("Column is full!")

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
            self.visualizer.draw(
                self.ui.screen, 
                self.agent.get_weights(), 
                self.history, 
                self.game_width
            )

            pygame.display.flip()
            self.ui.clock.tick(self.fps)

        return episode_score

    def run(self):
        episode = 0
        last_save = 0

        while episode < self.loop_count:
            self.reset_episode()
            reward = self.run_episode()
            self.history.append(reward)

            episode += 1
            last_save += 1

            if last_save >= self.save_every:
                self.agent.save(self.output_path)
                last_save = 0

            print(f"Episode {episode}/{self.loop_count} Score: {reward}")

        self.agent.save(self.output_path)


def run_ui_training():
    parser = argparse.ArgumentParser(description="M2MasterBot RL Training")
    parser.add_argument("--episodes", type=int, default=100, help="Number of episodes to train")
    parser.add_argument("--save-every", type=int, default=50, help="Save interval")
    parser.add_argument("--output-path", type=str, default="data/rl_agent.json", help="Path to save model")
    parser.add_argument("--fps", type=int, default=120, help="Training speed (FPS)")

    args = parser.parse_args()

    trainer = UITrainer(
        loop_count=args.episodes,
        save_every=args.save_every,
        output_path=args.output_path,
        fps=args.fps,
    )
    trainer.run()


if __name__ == "__main__":
    run_ui_training()

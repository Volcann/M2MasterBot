import os
from typing import List

from core.game_logic import GameLogic
from core.utils.utils import game_over, rearrange, remove_redundant
from deep_rl_agent.agent import RLAgent
from ui.game.game_ui import GameUI


class UITrainer:
    def __init__(
        self,
        loop_count: int = 500,
        save_every: int = 50,
        output_path: str = "data/rl_agent.json",
        fps: int = 20,
    ):
        self.loop_count = loop_count
        self.save_every = save_every
        self.output_path = output_path
        self.fps = fps
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self.agent = RLAgent()
        self.game = GameLogic()
        self.ui = GameUI(self.game)

        self.agent.load(output_path)

    def reset_episode(self):
        self.ui.reset_game()
        self.ui.next_value = self.game.get_random_value()

    def run_episode(self) -> float:
        rewards: List[float] = []
        while True:
            if game_over(self.game.get_matrix(), self.ui.next_value):
                self.ui.draw_game_over()
                if rewards:
                    self.agent.finish_episode(rewards)
                break

            self.ui.handle_events()

            if not self.ui.game_is_over and self.ui.input_column is None:
                matrix = self.game.get_matrix()
                try:
                    action = self.agent.select_action(matrix, self.ui.next_value)
                except Exception:
                    action = 0

                self.ui.input_column = action
                self.ui.trigger_drop_animation(action, self.ui.next_value)

            show_message = False

            if not self.ui.game_is_over and self.ui.input_column is not None:
                old_matrix = [row[:] for row in self.game.get_matrix()]
                merged, count = self.game.add_to_column(self.ui.next_value, self.ui.input_column)

                if not merged:
                    show_message = True
                    self.game.merge_column(self.ui.input_column)
                    self.ui.drop_animations = []
                else:
                    new_matrix = self.game.get_matrix()
                    self.ui.detect_and_trigger_animations(old_matrix, new_matrix, self.ui.input_column)
                    reward = float(count)
                    rewards.append(reward)
                    self.ui.next_value = self.game.get_random_value()
                    self.ui.input_column = None

            if show_message and not self.ui.game_is_over:
                self.ui.show_temp_message("Column is full!")

            matrix = self.game.get_matrix()
            matrix = rearrange(matrix)
            max_value = max(max(row) for row in matrix) if matrix else 0

            try:
                _, matrix = remove_redundant(matrix, max_value)
            except Exception:
                pass

            while True:
                merged, _ = self.game.merge_column()
                if not merged:
                    break
                matrix = rearrange(matrix)

            self.game.set_matrix(matrix)
            self.ui.draw_matrix()
            self.ui.clock.tick(self.fps)

        return sum(rewards)

    def run(self):
        episode = 0
        total_rewards = 0.0
        last_save = 0

        while episode < self.loop_count:
            self.reset_episode()
            episode_reward = self.run_episode()

            episode += 1
            total_rewards += episode_reward
            last_save += 1

            if last_save >= self.save_every:
                self.agent.save(self.output_path)
                last_save = 0

            self.ui.show_temp_message(
                f"Episode {episode}/{self.loop_count} reward {episode_reward:.1f}"
            )
            self.ui.clock.tick(10)

        self.agent.save(self.output_path)


def run_ui_training(
    loop_count: int = 500,
    save_every: int = 50,
    output_path: str = "data/rl_agent.json",
    fps: int = 50,
):
    trainer = UITrainer(
        loop_count=loop_count,
        save_every=save_every,
        output_path=output_path,
        fps=fps,
    )
    trainer.run()


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run_ui_training(loop_count=2000, save_every=25)

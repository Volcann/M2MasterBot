import os
import time
from typing import List
from core.game_logic import GameLogic
from deep_rl_agent.agent import RLAgent
from ui.game.game_ui import GameUI
from core.utils.utils import game_over, rearrange, remove_redundant


def run_ui_training(
    loop_count: int = 500,
    save_every: int = 50,
    output_path: str = "data/rl_agent.json",
    fps: int = 20,
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    agent = RLAgent()
    agent.load(output_path)
    game = GameLogic()
    ui = GameUI(game)
    episode = 0
    total_rewards = 0.0
    last_save = 0
    ui.clock.tick(fps)
    while episode < loop_count:
        ui.reset_game()
        ui.next_value = game.get_random_value()
        rewards: List[float] = []
        start_time = time.time()
        while True:
            if game_over(game.get_matrix(), ui.next_value):
                ui.draw_game_over()
                if rewards:
                    agent.finish_episode(rewards)
                break
            ui.handle_events()
            if not ui.game_is_over and ui.input_column is None:
                matrix = game.get_matrix()
                try:
                    action = agent.select_action(matrix, ui.next_value)
                except Exception:
                    action = 0
                ui.input_column = action
                ui.trigger_drop_animation(action, ui.next_value)
            show_message = False
            if not ui.game_is_over and ui.input_column is not None:
                old_matrix = [row[:] for row in game.get_matrix()]
                merged, count = game.add_to_column(ui.next_value, ui.input_column)
                if not merged:
                    show_message = True
                    game.merge_column(ui.input_column)
                    ui.drop_animations = []
                else:
                    new_matrix = game.get_matrix()
                    ui.detect_and_trigger_animations(old_matrix, new_matrix, ui.input_column)
                    reward = float(count)
                    rewards.append(reward)
                    ui.next_value = game.get_random_value()
                    ui.input_column = None
            if show_message and not ui.game_is_over:
                ui.show_temp_message("Column is full!")
            matrix = game.get_matrix()
            matrix = rearrange(matrix)
            max_value = max(max(row) for row in matrix) if matrix else 0
            try:
                _, matrix = remove_redundant(matrix, max_value)
            except Exception:
                pass
            while True:
                merged, _ = game.merge_column()
                if not merged:
                    break
                matrix = rearrange(matrix)
            game.set_matrix(matrix)
            ui.draw_matrix()
            ui.clock.tick(fps)
        episode += 1
        episode_reward = sum(rewards)
        total_rewards += episode_reward
        last_save += 1
        if last_save >= save_every:
            agent.save(output_path)
            last_save = 0
        ui.show_temp_message(f"Episode {episode}/{loop_count} reward {episode_reward:.1f}")
        ui.clock.tick(10)
    agent.save(output_path)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run_ui_training(loop_count=200, save_every=25)

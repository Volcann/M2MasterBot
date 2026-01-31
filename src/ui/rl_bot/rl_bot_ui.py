import pygame

from core.utils.utils import game_over, rearrange, remove_redundant
from core.game_logic import GameLogic
from deep_rl_agent.agent import RLAgent
from ui.game.game_ui import GameUI


class RLBotUI:
    def __init__(self, model_path: str, move_interval_ms: int = 800, fps: int = 30):
        self.model_path = model_path
        self.move_interval_ms = move_interval_ms
        self.fps = fps
        self.agent = RLAgent()
        self.game = GameLogic()
        self.ui = GameUI(self.game)
        self.last_action_time = 0

    def load_agent(self):
        self.agent.load(self.model_path)

    def reset(self):
        self.ui.reset_game()
        self.ui.next_value = self.game.get_random_value()
        self.last_action_time = pygame.time.get_ticks()

    def step(self):
        self.ui.handle_events()

        if self.ui.game_is_over:
            return False

        now = pygame.time.get_ticks()
        if self.ui.input_column is None and now - self.last_action_time >= self.move_interval_ms:
            action = self.agent.select_action(
                self.game.get_matrix(),
                self.ui.next_value,
                deterministic=True
            )
            self.ui.input_column = action
            self.last_action_time = now

        if self.ui.input_column is not None:
            col = self.ui.input_column
            next_val = self.ui.next_value

            old_matrix = [row[:] for row in self.game.get_matrix()]
            try:
                self.ui.trigger_drop_animation(col, next_val)
            except Exception:
                pass

            merged, _ = self.game.add_to_column(next_val, col)

            if not merged:
                self.ui.show_temp_message("Column full!")
                self.ui.input_column = None
            else:
                new_matrix = self.game.get_matrix()
                try:
                    self.ui.detect_and_trigger_animations(old_matrix, new_matrix, col)
                except Exception:
                    pass

                self.ui.next_value = self.game.get_random_value()
                self.ui.input_column = None

        self.ui.draw_matrix()
        self.ui.clock.tick(self.fps)

        return True

    def run(self):
        self.load_agent()
        self.reset()

        while True:
            if game_over(self.game.get_matrix(), self.ui.next_value):
                self.ui.draw_game_over()
                self.ui._save_game_over_to_csv()
                pygame.time.delay(2000)
                self.reset()

            if not self.step():
                break

            matrix = self.game.get_matrix()
            matrix = rearrange(matrix)
            max_value = max(max(row) for row in matrix)
            _, matrix = remove_redundant(matrix, max_value)

            while True:
                old_matrix = [row[:] for row in matrix]
                merged, _ = self.game.merge_column()
                if not merged:
                    break

                matrix = rearrange(self.game.get_matrix())
                try:
                    self.ui.detect_and_trigger_animations(old_matrix, matrix, None)
                except Exception:
                    pass

            self.game.set_matrix(matrix)

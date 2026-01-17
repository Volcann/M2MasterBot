import pygame

from game_ui.game_ui import GameUI
from M2Bot.game_bot.game_bot import GameBot


class BotGameUI(GameUI):
    def __init__(self, game_logic):
        super().__init__(game_logic)
        self.bot = GameBot()
        self.last_move_time = 0
        self.move_delay = 200

    def handle_events(self):
        super().handle_events()

        if not self.game_is_over and self.input_column is None:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time > self.move_delay:
                matrix = self.game_logic.get_matrix()
                best_col = self.bot.solve(matrix, self.next_value)
                self.input_column = best_col
                self.last_move_time = current_time

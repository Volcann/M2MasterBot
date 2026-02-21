import pygame

from ui.game.game_ui import GameUI
from heuristic_bot.bot import HeuristicBot
from heuristic_bot.debug.debug import Debugger


class HeuristicBotUI(GameUI):
    def __init__(self, game_logic):
        super().__init__(game_logic)
        self.bot = HeuristicBot()
        self.visualizer = Debugger(list(self.bot.weights.keys()))
        self.last_move_time = 0
        self.move_delay = 200
        self.debug = False

    def handle_events(self):
        super().handle_events()

        if not self.game_is_over and self.input_column is None:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time > self.move_delay:
                matrix = self.game_logic.get_matrix()
                self.visualizer = self.visualizer if self.debug else None
                best_col = self.bot.solve(matrix, self.next_value, self.visualizer)
                self.input_column = best_col
                self.last_move_time = current_time

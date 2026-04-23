import pygame
from ui.game.game_ui import GameUI
from agents.heuristic.fixed_linear import FixedLinearBot
from agents.heuristic.debug.debug import Debugger


class FixedLinearBotUI(GameUI):
    def __init__(self, game_logic):
        super().__init__(game_logic)
        self.bot = FixedLinearBot()
        self.visualizer = Debugger(list(self.bot.weights.keys()))
        self.last_move_time = 0
        self.move_delay = 2000  # Faster by default for bots
        self.debug = True

    def handle_events(self):
        super().handle_events()

        if not self.game_is_over and self.input_column is None:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time > self.move_delay:
                matrix = self.game_logic.get_matrix()
                visualizer = self.visualizer if self.debug else None
                best_col = self.bot.solve(matrix, self.next_value, visualizer)
                self.input_column = best_col
                self.last_move_time = current_time

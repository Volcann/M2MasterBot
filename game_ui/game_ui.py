import pygame
from config.constants import (
    CELL_SIZE, MARGIN, BG_COLOR,
    CELL_COLOR, TEXT_COLOR,
    FONT_SIZE, SCORE_FONT_SIZE,
    NEXT_FONT_SIZE, GRID_LENGTH,
    GRID_WIDTH
)


class GameUI:
    # M2-like color palette
    COLORS = {
        0: (25, 25, 25),        # empty
        2: (66, 133, 244),     # blue
        4: (255, 167, 38),     # orange
        8: (236, 64, 122),     # pink
        16: (0, 200, 83),      # green
        32: (156, 39, 176),    # purple
        64: (103, 58, 183),    # dark purple
        128: (205, 220, 57),   # yellow-green
        256: (244, 67, 54),    # red
        512: (0, 188, 212),    # cyan
        1024: (63, 81, 181),
        2048: (33, 150, 243),
    }

    BG_DARK = (15, 15, 15)
    GRID_BG = (35, 35, 35)
    TEXT_LIGHT = (245, 245, 245)

    def __init__(self, game_logic):
        self.game_logic = game_logic

        self.top_padding = 70
        self.bottom_padding = 110

        self.window_width = GRID_WIDTH * (CELL_SIZE + MARGIN) + MARGIN
        self.window_height = (
            GRID_LENGTH * (CELL_SIZE + MARGIN)
            + self.top_padding
            + self.bottom_padding
        )

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height)
        )
        pygame.display.set_caption("M2 Block")

        self.font = pygame.font.SysFont("Arial", FONT_SIZE, bold=True)
        self.score_font = pygame.font.SysFont("Arial", SCORE_FONT_SIZE, bold=True)
        self.next_font = pygame.font.SysFont("Arial", NEXT_FONT_SIZE, bold=True)

        self.clock = pygame.time.Clock()
        self.input_column = None
        self.next_value = self.game_logic.random_value()

        self.temp_message = None
        self.temp_message_time = 0
        self.temp_message_duration = 1500

    def show_temp_message(self, text):
        self.temp_message = text
        self.temp_message_time = pygame.time.get_ticks()

    def draw_rounded_rect(self, surface, color, rect, radius=12):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_matrix(self):
        self.screen.fill(self.BG_DARK)

        # Grid background
        grid_rect = pygame.Rect(
            MARGIN,
            self.top_padding,
            GRID_WIDTH * (CELL_SIZE + MARGIN) - MARGIN,
            GRID_LENGTH * (CELL_SIZE + MARGIN) - MARGIN
        )
        self.draw_rounded_rect(self.screen, self.GRID_BG, grid_rect, 16)

        matrix = self.game_logic._matrix

        for row in range(GRID_LENGTH):
            for col in range(GRID_WIDTH):
                value = matrix[row][col]

                rect = pygame.Rect(
                    MARGIN + col * (CELL_SIZE + MARGIN),
                    self.top_padding + MARGIN + row * (CELL_SIZE + MARGIN),
                    CELL_SIZE,
                    CELL_SIZE
                )

                color = self.COLORS.get(value, CELL_COLOR)
                self.draw_rounded_rect(self.screen, color, rect, 14)

                if value != 0:
                    font = self.font
                    if value >= 512:
                        font = pygame.font.SysFont("Arial", FONT_SIZE - 6, bold=True)

                    text_surface = font.render(str(value), True, self.TEXT_LIGHT)
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)

        # Score (Top Center)
        score_surface = self.score_font.render(
            f"Score {self.game_logic.get_score()}",
            True,
            self.TEXT_LIGHT
        )
        self.screen.blit(
            score_surface,
            score_surface.get_rect(center=(self.window_width // 2, 30))
        )

        # Next block tile (Bottom Center)
        next_rect = pygame.Rect(
            (self.window_width - CELL_SIZE) // 2,
            self.window_height - CELL_SIZE - 25,
            CELL_SIZE,
            CELL_SIZE
        )
        next_color = self.COLORS.get(self.next_value, CELL_COLOR)
        self.draw_rounded_rect(self.screen, next_color, next_rect, 14)

        next_text = self.font.render(str(self.next_value), True, self.TEXT_LIGHT)
        self.screen.blit(
            next_text,
            next_text.get_rect(center=next_rect.center)
        )

        self.draw_temp_message()
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.KEYDOWN:
                for i in range(GRID_WIDTH):
                    if event.key == getattr(pygame, f'K_{i}'):
                        self.input_column = i

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if y >= self.top_padding:
                        col = (x - MARGIN) // (CELL_SIZE + MARGIN)
                        if 0 <= col < GRID_WIDTH:
                            self.input_column = col

    def draw_game_over(self):
        overlay = pygame.Surface(
            (self.window_width, self.window_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont("Arial", 64, bold=True)
        text = font.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(
            text,
            text.get_rect(center=(self.window_width // 2, self.window_height // 2))
        )
        pygame.display.flip()

    def draw_temp_message(self):
        if not self.temp_message:
            return

        if pygame.time.get_ticks() - self.temp_message_time > self.temp_message_duration:
            self.temp_message = None
            return

        msg_surface = self.font.render(self.temp_message, True, (255, 120, 120))
        self.screen.blit(
            msg_surface,
            msg_surface.get_rect(
                center=(self.window_width // 2, self.window_height - 70)
            )
        )

    def run(self):
        game_is_over = False

        while True:
            self.handle_events()
            show_message = False

            if not game_is_over and self.input_column is not None:
                if not self.game_logic.add_to_column(
                    self.next_value, self.input_column
                ):
                    show_message = True
                else:
                    self.next_value = self.game_logic.random_value()
                    self.input_column = None

            if show_message:
                self.show_temp_message("Column is full")

            if self.game_logic.game_over(self.next_value):
                game_is_over = True
                self.draw_game_over()

            self.draw_matrix()
            self.clock.tick(30)

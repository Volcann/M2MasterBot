import pygame
import math
import colorsys

from config.constants import (
    CELL_SIZE, MARGIN,
    SCORE_FONT_SIZE,
    GRID_LENGTH,
    GRID_WIDTH
)
from core.utils.utils import game_over, rearrange


class GameUI:
    BASE_COLORS = {
        0: (25, 25, 25),
        2: (66, 133, 244),
        4: (255, 167, 38),
        8: (236, 64, 122),
        16: (0, 200, 83),
        32: (156, 39, 176),
        64: (103, 58, 183),
        128: (205, 220, 57),
        256: (244, 67, 54),
        512: (0, 188, 212),
        1024: (63, 81, 181),
        2048: (255, 215, 0),
    }

    BG_DARK = (12, 12, 15)
    GRID_BG = (28, 28, 35)
    TEXT_LIGHT = (245, 245, 245)
    TEXT_DIM = (150, 150, 160)
    ACCENT = (100, 180, 255)
    ACCENT_HOVER = (130, 200, 255)
    BUTTON_BG = (45, 45, 55)
    BUTTON_HOVER = (60, 60, 75)

    def __init__(self, game_logic):
        self.game_logic = game_logic

        self.top_padding = 90
        self.bottom_padding = 140

        self.window_width = GRID_WIDTH * (CELL_SIZE + MARGIN) + MARGIN
        self.window_height = (
            GRID_LENGTH * (CELL_SIZE + MARGIN)
            + self.top_padding
            + self.bottom_padding
        )

        pygame.init()
        self.is_fullscreen = False
        self.base_width = self.window_width
        self.base_height = self.window_height
        self.scale_factor = 1.0
        self.screen_offset = (0, 0)

        self.render_surface = pygame.Surface((self.base_width, self.base_height))

        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("M2 Block")
        self.fonts = {
            size: pygame.font.SysFont("Arial", size, bold=True)
            for size in range(12, 45, 2)
        }
        self.score_font = pygame.font.SysFont("Arial", SCORE_FONT_SIZE, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.game_over_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.sub_font = pygame.font.SysFont("Arial", 20)

        self.clock = pygame.time.Clock()
        self.input_column = None
        self.next_value = self.game_logic.get_random_value()
        self.game_is_over = False

        self.hover_column = -1
        self.mouse_pos = (0, 0)
        self.high_score = 0
        self.merge_animations = []
        self.pulse_animations = []
        self.drop_animations = []
        self.prev_matrix = None

        self.temp_message = None
        self.temp_message_time = 0
        self.temp_message_duration = 1500

        self.restart_button_rect = None
        self.fullscreen_button_rect = None
        self.game_over_time = None

    def get_cell_color(self, value):
        if value == 0:
            return self.BASE_COLORS[0]
        if value in self.BASE_COLORS:
            return self.BASE_COLORS[value]
        power = int(math.log2(value)) if value > 0 else 0

        hue = ((power - 12) * 0.08) % 1.0
        saturation = 0.75 + 0.15 * math.sin(power * 0.5)
        value_hsv = 0.85 + 0.1 * math.cos(power * 0.3)

        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value_hsv)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_font_for_value(self, value, max_width):
        text = str(value)
        padding = 10
        available_width = max_width - padding * 2

        for size in range(44, 10, -2):
            if size in self.fonts:
                font = self.fonts[size]
                text_width = font.size(text)[0]
                if text_width <= available_width:
                    return font

        return self.fonts[12]

    def show_temp_message(self, text):
        self.temp_message = text
        self.temp_message_time = pygame.time.get_ticks()

    def draw_rounded_rect(self, surface, color, rect, radius=12):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_glow_rect(self, surface, color, rect, radius=12, glow_size=3):
        glow_color = tuple(min(255, c + 40) for c in color)
        glow_rect = rect.inflate(glow_size, glow_size)
        pygame.draw.rect(surface, glow_color, glow_rect, border_radius=radius + 2, width=2)
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_header(self):
        title = self.title_font.render("M2 BLOCK", True, self.ACCENT)
        self.render_surface.blit(title, (15, 15))

        score = self.game_logic.get_score()
        score_text = f"{score:,}"

        if score >= 10000000:
            score_font = pygame.font.SysFont("Arial", 16, bold=True)
        elif score >= 1000000:
            score_font = pygame.font.SysFont("Arial", 20, bold=True)
        elif score >= 100000:
            score_font = pygame.font.SysFont("Arial", 24, bold=True)
        else:
            score_font = self.score_font

        score_label = pygame.font.SysFont("Arial", 14).render("SCORE", True, self.TEXT_DIM)
        score_value = score_font.render(score_text, True, self.TEXT_LIGHT)

        label_x = self.window_width - score_label.get_width() - 10
        value_x = self.window_width - score_value.get_width() - 10
        self.render_surface.blit(score_label, (label_x, 15))
        self.render_surface.blit(score_value, (value_x, 32))

        high_text = f"{self.high_score:,}"
        if self.high_score >= 100000:
            high_font = pygame.font.SysFont("Arial", 16, bold=True)
        else:
            high_font = self.button_font

        high_label = pygame.font.SysFont("Arial", 14).render("BEST", True, self.TEXT_DIM)
        high_value = high_font.render(high_text, True, self.ACCENT)

        center_x = self.window_width // 2
        self.render_surface.blit(high_label, (center_x - high_label.get_width() // 2, 15))
        self.render_surface.blit(high_value, (center_x - high_value.get_width() // 2, 32))

    def draw_column_hover(self):
        if self.hover_column >= 0 and not self.game_is_over:
            x = MARGIN + self.hover_column * (CELL_SIZE + MARGIN)
            indicator_rect = pygame.Rect(x, self.top_padding - 8, CELL_SIZE, 4)
            pygame.draw.rect(self.render_surface, self.ACCENT_HOVER, indicator_rect, border_radius=2)

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def ease_out_elastic(self, t):
        if t == 0 or t == 1:
            return t
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1

    def draw_matrix(self):
        self.render_surface.fill(self.BG_DARK)
        self.draw_header()

        grid_rect = pygame.Rect(
            MARGIN - 2, self.top_padding - 2,
            GRID_WIDTH * (CELL_SIZE + MARGIN) - MARGIN + 4,
            GRID_LENGTH * (CELL_SIZE + MARGIN) - MARGIN + 4
        )
        pygame.draw.rect(self.render_surface, (40, 40, 50), grid_rect, border_radius=18)
        inner_grid = pygame.Rect(
            MARGIN, self.top_padding,
            GRID_WIDTH * (CELL_SIZE + MARGIN) - MARGIN,
            GRID_LENGTH * (CELL_SIZE + MARGIN) - MARGIN
        )
        self.draw_rounded_rect(self.render_surface, self.GRID_BG, inner_grid, 16)
        self.draw_column_hover()

        matrix = self.game_logic.get_matrix()
        current_time = pygame.time.get_ticks()

        for row in range(GRID_LENGTH):
            for col in range(GRID_WIDTH):
                rect = pygame.Rect(
                    MARGIN + col * (CELL_SIZE + MARGIN),
                    self.top_padding + MARGIN + row * (CELL_SIZE + MARGIN),
                    CELL_SIZE, CELL_SIZE
                )
                self.draw_rounded_rect(self.render_surface, self.BASE_COLORS[0], rect, 14)

        for anim in self.merge_animations[:]:
            from_col, from_row, to_col, to_row, start_time, value = anim
            elapsed = current_time - start_time
            duration = 200

            if elapsed >= duration:
                self.merge_animations.remove(anim)
                continue

            progress = self.ease_out_cubic(elapsed / duration)
            start_x = MARGIN + from_col * (CELL_SIZE + MARGIN)
            start_y = self.top_padding + MARGIN + from_row * (CELL_SIZE + MARGIN)
            end_x = MARGIN + to_col * (CELL_SIZE + MARGIN)
            end_y = self.top_padding + MARGIN + to_row * (CELL_SIZE + MARGIN)

            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress

            scale = 1.0 - 0.6 * progress
            alpha = int(255 * (1 - progress * 0.5))

            scaled_size = int(CELL_SIZE * scale)
            offset = (CELL_SIZE - scaled_size) // 2

            rect = pygame.Rect(
                current_x + offset, current_y + offset,
                scaled_size, scaled_size
            )

            color = self.get_cell_color(value)
            temp_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, (*color, alpha), 
                           (0, 0, scaled_size, scaled_size), border_radius=int(14 * scale))
            self.render_surface.blit(temp_surface, rect.topleft)

            if scaled_size > 30:
                font = self.get_font_for_value(value, scaled_size)
                text_surface = font.render(str(value), True, (*self.TEXT_LIGHT[:3], alpha))
                text_rect = text_surface.get_rect(center=rect.center)
                temp_text = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                temp_text.blit(text_surface, (0, 0))
                temp_text.set_alpha(alpha)
                self.render_surface.blit(temp_text, text_rect)

        for anim in self.drop_animations[:]:
            col, current_y, target_y, value, start_time = anim
            elapsed = current_time - start_time
            duration = 150

            if elapsed >= duration:
                self.drop_animations.remove(anim)
                continue

            progress = self.ease_out_cubic(elapsed / duration)
            y = current_y + (target_y - current_y) * progress

            x = MARGIN + col * (CELL_SIZE + MARGIN)
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            color = self.get_cell_color(value)
            self.draw_glow_rect(self.render_surface, color, rect, 14)

            font = self.get_font_for_value(value, CELL_SIZE)
            text_surface = font.render(str(value), True, self.TEXT_LIGHT)
            text_rect = text_surface.get_rect(center=rect.center)
            self.render_surface.blit(text_surface, text_rect)

        for row in range(GRID_LENGTH):
            for col in range(GRID_WIDTH):
                value = matrix[row][col]
                if value == 0:
                    continue

                base_x = MARGIN + col * (CELL_SIZE + MARGIN)
                base_y = self.top_padding + MARGIN + row * (CELL_SIZE + MARGIN)

                scale = 1.0
                for anim in self.pulse_animations:
                    anim_col, anim_row, start_time, _ = anim
                    if anim_col == col and anim_row == row:
                        elapsed = current_time - start_time
                        if elapsed < 300:
                            progress = elapsed / 300
                            scale = 1.0 + 0.2 * math.sin(progress * math.pi) * (1 - progress)

                if scale != 1.0:
                    scaled_size = int(CELL_SIZE * scale)
                    offset = (CELL_SIZE - scaled_size) // 2
                    rect = pygame.Rect(
                        base_x + offset, base_y + offset,
                        scaled_size, scaled_size
                    )
                else:
                    rect = pygame.Rect(base_x, base_y, CELL_SIZE, CELL_SIZE)

                color = self.get_cell_color(value)
                self.draw_glow_rect(self.render_surface, color, rect, 14)

                font = self.get_font_for_value(value, rect.width)
                text_surface = font.render(str(value), True, self.TEXT_LIGHT)
                text_rect = text_surface.get_rect(center=rect.center)
                self.render_surface.blit(text_surface, text_rect)

        self.pulse_animations = [
            a for a in self.pulse_animations 
            if current_time - a[2] < 300
        ]

        self.draw_bottom_section()
        self.draw_temp_message()
        if self.is_fullscreen or self.scale_factor != 1.0:
            self.screen.fill(self.BG_DARK)
            scaled_surface = pygame.transform.smoothscale(
                self.render_surface,
                (int(self.base_width * self.scale_factor), 
                 int(self.base_height * self.scale_factor))
            )
            self.screen.blit(scaled_surface, self.screen_offset)
        else:
            self.screen.blit(self.render_surface, (0, 0))

        pygame.display.flip()

    def draw_bottom_section(self):
        next_label = self.sub_font.render("NEXT", True, self.TEXT_DIM)
        label_x = (self.window_width - next_label.get_width()) // 2
        self.render_surface.blit(next_label, (label_x, self.window_height - CELL_SIZE - 70))

        next_rect = pygame.Rect(
            (self.window_width - CELL_SIZE) // 2,
            self.window_height - CELL_SIZE - 40,
            CELL_SIZE, CELL_SIZE
        )
        next_color = self.get_cell_color(self.next_value)
        self.draw_glow_rect(self.render_surface, next_color, next_rect, 14)

        font = self.get_font_for_value(self.next_value, CELL_SIZE)
        next_text = font.render(str(self.next_value), True, self.TEXT_LIGHT)
        self.render_surface.blit(next_text, next_text.get_rect(center=next_rect.center))
        button_width, button_height = 100, 36
        self.restart_button_rect = pygame.Rect(
            (self.window_width - button_width) // 2,
            self.window_height - 35,
            button_width, button_height
        )

        is_hover = self.restart_button_rect.collidepoint(self.mouse_pos)
        button_color = self.BUTTON_HOVER if is_hover else self.BUTTON_BG

        pygame.draw.rect(self.render_surface, button_color, self.restart_button_rect, border_radius=8)
        pygame.draw.rect(self.render_surface, self.ACCENT, self.restart_button_rect, width=2, border_radius=8)
        restart_text = self.button_font.render("RESTART", True, self.ACCENT)
        self.render_surface.blit(restart_text, restart_text.get_rect(center=self.restart_button_rect.center))

    def handle_events(self):
        self.mouse_pos = self.get_game_mouse_pos()
        x, y = self.mouse_pos
        if self.top_padding <= y < self.top_padding + GRID_LENGTH * (CELL_SIZE + MARGIN):
            col = (x - MARGIN) // (CELL_SIZE + MARGIN)
            self.hover_column = col if 0 <= col < GRID_WIDTH else -1
        else:
            self.hover_column = -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.VIDEORESIZE:
                new_width, new_height = event.size
                self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                scale_x = new_width / self.base_width
                scale_y = new_height / self.base_height
                self.scale_factor = min(scale_x, scale_y)

                scaled_w = int(self.base_width * self.scale_factor)
                scaled_h = int(self.base_height * self.scale_factor)
                self.screen_offset = ((new_width - scaled_w) // 2, (new_height - scaled_h) // 2)
                self.is_fullscreen = (new_width != self.base_width or new_height != self.base_height)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

                for i in range(GRID_WIDTH):
                    if event.key == getattr(pygame, f'K_{i}'):
                        self.input_column = i

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_x = (event.pos[0] - self.screen_offset[0]) / self.scale_factor
                    click_y = (event.pos[1] - self.screen_offset[1]) / self.scale_factor

                    if self.restart_button_rect and self.restart_button_rect.collidepoint((click_x, click_y)):
                        self.reset_game()
                        return

                    if click_y >= self.top_padding:
                        col = int((click_x - MARGIN) // (CELL_SIZE + MARGIN))
                        if 0 <= col < GRID_WIDTH:
                            self.input_column = col

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            info = pygame.display.Info()
            screen_w, screen_h = info.current_w, info.current_h

            scale_x = screen_w / self.base_width
            scale_y = screen_h / self.base_height
            self.scale_factor = min(scale_x, scale_y)
            scaled_w = int(self.base_width * self.scale_factor)
            scaled_h = int(self.base_height * self.scale_factor)
            self.screen_offset = ((screen_w - scaled_w) // 2, (screen_h - scaled_h) // 2)

            self.screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
        else:
            self.scale_factor = 1.0
            self.screen_offset = (0, 0)
            self.screen = pygame.display.set_mode((self.base_width, self.base_height))

    def get_game_mouse_pos(self):
        mx, my = pygame.mouse.get_pos()
        gx = (mx - self.screen_offset[0]) / self.scale_factor
        gy = (my - self.screen_offset[1]) / self.scale_factor
        return (int(gx), int(gy))

    def reset_game(self):
        current_score = self.game_logic.get_score()
        if current_score > self.high_score:
            self.high_score = current_score

        self.game_logic.reset()
        self.game_is_over = False
        self.input_column = None
        self.next_value = self.game_logic.get_random_value()
        self.merge_animations = []
        self.pulse_animations = []
        self.drop_animations = []
        self.prev_matrix = None
        self.temp_message = None
        self.temp_message_time = 0
        self.game_over_time = None

    def draw_game_over(self):
        overlay = pygame.Surface(
            (self.window_width, self.window_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 200))
        self.render_surface.blit(overlay, (0, 0))

        shadow = self.game_over_font.render("GAME OVER", True, (40, 40, 40))
        text = self.game_over_font.render("GAME OVER", True, (255, 100, 100))

        center_x = self.window_width // 2
        center_y = self.window_height // 2 - 40
        self.render_surface.blit(shadow, shadow.get_rect(center=(center_x + 3, center_y + 3)))
        self.render_surface.blit(text, text.get_rect(center=(center_x, center_y)))

        score_text = self.score_font.render(
            f"Score: {self.game_logic.get_score():,}", True, self.TEXT_LIGHT
        )
        self.render_surface.blit(score_text, score_text.get_rect(center=(center_x, center_y + 50)))

        if self.game_over_time:
            elapsed_ms = pygame.time.get_ticks() - self.game_over_time
            seconds_left = max(0, 5 - (elapsed_ms // 1000))
            hint_text = self.sub_font.render(
                f"Restarting in {seconds_left}...", True, self.TEXT_DIM
            )
        else:
            hint_text = self.sub_font.render(
                "Click RESTART or press R", True, self.TEXT_DIM
            )

        self.render_surface.blit(hint_text, hint_text.get_rect(center=(center_x, center_y + 90)))
        pygame.display.flip()

    def draw_temp_message(self):
        if not self.temp_message:
            return

        if pygame.time.get_ticks() - self.temp_message_time > self.temp_message_duration:
            self.temp_message = None
            return

        msg_surface = self.button_font.render(self.temp_message, True, (255, 150, 150))
        self.render_surface.blit(
            msg_surface,
            msg_surface.get_rect(center=(15 + msg_surface.get_width() // 2, self.window_height - 25))
        )

    def trigger_drop_animation(self, col, value):
        matrix = self.game_logic.get_matrix()
        target_row = 0
        for row in range(GRID_LENGTH):
            if matrix[row][col] == 0:
                target_row = row
                break
            elif row == GRID_LENGTH - 1:
                target_row = row

        start_y = self.window_height - self.bottom_padding + CELL_SIZE
        target_y = self.top_padding + MARGIN + target_row * (CELL_SIZE + MARGIN)
        self.drop_animations.append((col, start_y, target_y, value, pygame.time.get_ticks()))

    def detect_and_trigger_animations(self, old_matrix, new_matrix, merged_col):
        current_time = pygame.time.get_ticks()

        if old_matrix is None:
            return

        target_cells = {}
        for row in range(GRID_LENGTH):
            for col in range(GRID_WIDTH):
                old_val = old_matrix[row][col]
                new_val = new_matrix[row][col]

                if new_val != 0 and new_val != old_val and new_val > old_val:
                    target_cells[(col, row)] = new_val
                    self.pulse_animations.append((col, row, current_time + 200, new_val))

        for row in range(GRID_LENGTH):
            for col in range(GRID_WIDTH):
                old_val = old_matrix[row][col]
                new_val = new_matrix[row][col]

                if old_val != 0 and new_val == 0:
                    best_target = None
                    best_dist = float('inf')

                    for (t_col, t_row), t_val in target_cells.items():
                        if t_val >= old_val * 2:
                            dist = abs(col - t_col) + abs(row - t_row)
                            if dist < best_dist:
                                best_dist = dist
                                best_target = (t_col, t_row)

                    if best_target:
                        self.merge_animations.append(
                            (col, row, best_target[0], best_target[1], current_time, old_val)
                        )

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            matrix = self.game_logic.get_matrix()
            if game_over(matrix, self.next_value):
                if not self.game_is_over:
                    self.game_is_over = True
                    if self.game_logic.get_score() > self.high_score:
                        self.high_score = self.game_logic.get_score()
                    self.game_over_time = pygame.time.get_ticks()

                if self.game_over_time and (current_time - self.game_over_time) >= 2000:
                    self.reset_game()
                    self.clock.tick(60)
                    continue

                self.draw_game_over()
                self.handle_events()
                self.clock.tick(60)
                continue

            self.handle_events()
            show_message = False

            if not self.game_is_over and self.input_column is not None:
                old_matrix = [row[:] for row in matrix]
                self.trigger_drop_animation(self.input_column, self.next_value)

                merged, count = self.game_logic.add_to_column(
                    self.next_value, self.input_column
                )

                if not merged:
                    show_message = True
                    self.game_logic.merge_column(self.input_column)
                    self.drop_animations = []
                else:
                    new_matrix = self.game_logic.get_matrix()
                    self.detect_and_trigger_animations(old_matrix, new_matrix, self.input_column)

                    self.next_value = self.game_logic.get_random_value()
                    self.input_column = None

            if show_message:
                self.show_temp_message("Column is full!")

            matrix = self.game_logic.get_matrix()
            matrix = rearrange(matrix)
            self.game_logic.set_matrix(matrix)
            self.draw_matrix()
            self.clock.tick(60)

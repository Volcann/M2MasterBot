import pygame
import numpy as np


class RLVisualizer:
    def __init__(self, feature_names: list, width: int = 350):
        self.feature_names = feature_names
        self.width = width
        self.font = pygame.font.SysFont("Arial", 16)
        self.header_font = pygame.font.SysFont("Arial", 20, bold=True)

    def draw(self, screen, theta, history, x_offset):
        rect = pygame.Rect(x_offset, 0, self.width, screen.get_height())
        pygame.draw.rect(screen, (25, 25, 30), rect)

        y = 40
        title = self.header_font.render("AGENT WITH TEACHER", True, (255, 255, 255))
        screen.blit(title, (x_offset + 20, y))
        y += 40

        max_w = np.max(np.abs(theta)) if np.max(np.abs(theta)) > 0 else 1.0
        for i, name in enumerate(self.feature_names):
            val = theta[i]
            label = self.font.render(f"{name}: {val:.3f}", True, (200, 200, 200))
            screen.blit(label, (x_offset + 20, y))

            bar_w = int((val / max_w) * 100)
            color = (0, 200, 255) if val > 0 else (255, 80, 80)
            pygame.draw.rect(screen, (50, 50, 50), (x_offset + 150, y + 5, 100, 10))
            pygame.draw.rect(screen, color, (x_offset + 150, y + 5, abs(bar_w), 10))
            y += 30

        y += 50
        graph_title = self.header_font.render("REWARD HISTORY", True, (255, 255, 255))
        screen.blit(graph_title, (x_offset + 20, y))

        graph_rect = pygame.Rect(x_offset + 20, y + 30, 310, 150)
        pygame.draw.rect(screen, (15, 15, 20), graph_rect)

        if len(history) > 1:
            data = history[-50:]
            h_max, h_min = max(data), min(data)
            diff = h_max - h_min if h_max != h_min else 1
            points = []
            for i, val in enumerate(data):
                px = x_offset + 20 + (i * (310 / (len(data) - 1)))
                py = (y + 180) - ((val - h_min) / diff * 140)
                points.append((int(px), int(py)))
            pygame.draw.lines(screen, (0, 255, 150), False, points, 2)

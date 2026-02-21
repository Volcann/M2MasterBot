import pygame
import numpy as np


class NoTeacherVisualizer:
    def __init__(self, feature_names: list, width: int = 350):
        self.feature_names = feature_names
        self.width = width
        self.font = pygame.font.SysFont("Arial", 16)
        self.header_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.alert_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        self.weight_changes = []

    def draw(self, screen, theta, history, epsilon, weight_volatility, x_offset):
        rect = pygame.Rect(x_offset, 0, self.width, screen.get_height())
        pygame.draw.rect(screen, (25, 25, 30), rect)

        y = 30
        title = self.header_font.render("NO-TEACHER AGENT", True, (255, 255, 255))
        screen.blit(title, (x_offset + 20, y))
        y += 40

        # --- Epsilon / Exploration Bar ---
        eps_label = self.font.render(f"EXPLORATION (ε): {epsilon:.3f}", True, (200, 200, 200))
        screen.blit(eps_label, (x_offset + 20, y))
        y += 25
        pygame.draw.rect(screen, (50, 50, 50), (x_offset + 20, y, 310, 15))
        pygame.draw.rect(screen, (0, 255, 100), (x_offset + 20, y, int(310 * epsilon), 15))
        y += 35

        # --- Agent Weights ---
        max_w = np.max(np.abs(theta)) if np.max(np.abs(theta)) > 0 else 1.0
        for i, name in enumerate(self.feature_names):
            val = theta[i]
            label = self.font.render(f"{name}: {val:.3f}", True, (200, 200, 200))
            screen.blit(label, (x_offset + 20, y))

            bar_w = int((val / max_w) * 100)
            color = (0, 200, 255) if val > 0 else (255, 80, 80)
            pygame.draw.rect(screen, (50, 50, 50), (x_offset + 150, y + 5, 100, 10))
            pygame.draw.rect(screen, color, (x_offset + 150, y + 5, abs(bar_w), 10))
            y += 25

        y += 20
        # --- Stability Metrics / Collapse Warning ---
        if len(history) > 10:
            recent_avg = np.mean(history[-10:])
            all_time_max = max(history)
            
            status = "STABLE"
            color = (0, 255, 0)
            
            if recent_avg < (all_time_max * 0.2) and all_time_max > 2:
                status = "COLLAPSED (FORGETTING)"
                color = (255, 0, 0)
            elif recent_avg < (all_time_max * 0.6) and all_time_max > 2:
                status = "DRIFTING / DEGRADING"
                color = (255, 165, 0)

            status_label = self.alert_font.render(status, True, color)
            screen.blit(status_label, (x_offset + 20, y))
        y += 40

        # --- Weight Volatility Sparkline ---
        volt_title = self.header_font.render("WEIGHT VOLATILITY", True, (255, 255, 255))
        screen.blit(volt_title, (x_offset + 20, y))
        y += 30
        
        volt_rect = pygame.Rect(x_offset + 20, y, 310, 80)
        pygame.draw.rect(screen, (15, 15, 20), volt_rect)
        
        self.weight_changes.append(weight_volatility)
        if len(self.weight_changes) > 50:
            self.weight_changes.pop(0)

        if len(self.weight_changes) > 1:
            data = self.weight_changes
            v_max = max(data) if max(data) > 0 else 1.0
            points = []
            for i, val in enumerate(data):
                px = x_offset + 20 + (i * (310 / (len(data) - 1)))
                py = (y + 80) - (val / v_max * 75)
                points.append((int(px), int(py)))
            pygame.draw.lines(screen, (255, 200, 0), False, points, 2)
        y += 100

        # --- Reward History ---
        graph_title = self.header_font.render("REWARD HISTORY", True, (255, 255, 255))
        screen.blit(graph_title, (x_offset + 20, y))
        y += 30

        graph_rect = pygame.Rect(x_offset + 20, y, 310, 100)
        pygame.draw.rect(screen, (15, 15, 20), graph_rect)

        if len(history) > 1:
            data = history[-50:]
            h_max, h_min = max(data), min(data)
            diff = h_max - h_min if h_max != h_min else 1
            points = []
            for i, val in enumerate(data):
                px = x_offset + 20 + (i * (310 / (len(data) - 1)))
                py = (y + 100) - ((val - h_min) / diff * 90)
                points.append((int(px), int(py)))
            pygame.draw.lines(screen, (0, 255, 150), False, points, 2)

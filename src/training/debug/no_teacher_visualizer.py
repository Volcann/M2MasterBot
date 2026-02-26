import pygame
import numpy as np


class NoTeacherVisualizer:
    def __init__(self, feature_names: list, width: int = 400):
        self.feature_names = feature_names
        self.width = width
        self.font = pygame.font.SysFont("Arial", 14)
        self.header_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.alert_font = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.weight_changes = []

    def _draw_gradient_bar(self, screen, x, y, w, h, val, max_val):
        """Draws a premium gradient-style bar."""
        pygame.draw.rect(screen, (40, 40, 45), (x, y, w, h))
        if max_val == 0: return
        
        fill_w = int(abs(val / max_val) * w)
        fill_w = min(fill_w, w)
        
        if val > 0:
            # Cyan to Blue gradient
            for i in range(fill_w):
                color = (0, 200 - i * 50 // w, 255)
                pygame.draw.line(screen, color, (x + i, y), (x + i, y + h))
        else:
            # Red to Orange gradient
            for i in range(fill_w):
                color = (255, 80 + i * 40 // w, 80)
                pygame.draw.line(screen, color, (x + i, y), (x + i, y + h))

    def draw(self, screen, theta, history, epsilon, weight_volatility, x_offset):
        rect = pygame.Rect(x_offset, 0, self.width, screen.get_height())
        pygame.draw.rect(screen, (20, 20, 25), rect)
        pygame.draw.line(screen, (50, 50, 60), (x_offset, 0), (x_offset, screen.get_height()), 2)

        y = 30
        title = self.header_font.render("NO-TEACHER AGENT (SCRATCH)", True, (255, 100, 0))
        screen.blit(title, (x_offset + 20, y))
        y += 40

        # --- Epsilon / Exploration Bar ---
        eps_label = self.font.render(f"EXPLORATION (ε): {epsilon:.3f}", True, (150, 150, 160))
        screen.blit(eps_label, (x_offset + 20, y))
        y += 25
        pygame.draw.rect(screen, (40, 40, 45), (x_offset + 20, y, 360, 15))
        pygame.draw.rect(screen, (255, 200, 0), (x_offset + 20, y, int(360 * epsilon), 15))
        y += 35

        # --- Agent Weights ---
        weight_title = self.header_font.render("AGENT WEIGHTS", True, (255, 255, 255))
        screen.blit(weight_title, (x_offset + 20, y))
        y += 35

        max_w = np.max(np.abs(theta)) if np.max(np.abs(theta)) > 0 else 1.0
        for i, name in enumerate(self.feature_names):
            val = theta[i]
            label = self.font.render(name.upper(), True, (180, 180, 190))
            screen.blit(label, (x_offset + 20, y))

            self._draw_gradient_bar(screen, x_offset + 120, y, 200, 12, val, max_w)
            
            val_text = self.font.render(f"{val:+.3f}", True, (220, 220, 230))
            screen.blit(val_text, (x_offset + 330, y - 2))
            y += 28

        y += 20
        # --- Stability Metrics / Collapse Warning ---
        if len(history) > 10:
            recent_avg = np.mean(history[-10:])
            all_time_max = max(history)
            
            status = "STABLE"
            color = (0, 255, 100)
            
            if recent_avg < (all_time_max * 0.2) and all_time_max > 2:
                status = "COLLAPSED (FORGETTING)"
                color = (255, 50, 50)
            elif recent_avg < (all_time_max * 0.6) and all_time_max > 2:
                status = "DRIFTING / DEGRADING"
                color = (255, 150, 0)

            status_box = pygame.Rect(x_offset + 20, y, 360, 40)
            pygame.draw.rect(screen, (30, 30, 35), status_box, border_radius=5)
            status_label = self.alert_font.render(status, True, color)
            screen.blit(status_label, (x_offset + 40, y + 8))
        y += 60

        # --- Weight Volatility Sparkline ---
        volt_title = self.header_font.render("WEIGHT VOLATILITY (ΔW)", True, (255, 255, 255))
        screen.blit(volt_title, (x_offset + 20, y))
        y += 30
        
        volt_rect = pygame.Rect(x_offset + 20, y, 360, 80)
        pygame.draw.rect(screen, (15, 15, 18), volt_rect)
        pygame.draw.rect(screen, (40, 40, 45), volt_rect, 1)
        
        self.weight_changes.append(weight_volatility)
        if len(self.weight_changes) > 100:
            self.weight_changes.pop(0)

        if len(self.weight_changes) > 1:
            data = self.weight_changes
            v_max = max(data) if max(data) > 0 else 1.0
            points = []
            for i, val in enumerate(data):
                px = x_offset + 20 + (i * (360 / (len(data) - 1)))
                py = (y + 80) - (val / v_max * 70 + 5)
                points.append((int(px), int(py)))
            pygame.draw.lines(screen, (255, 255, 0), False, points, 2)
        y += 100

        # --- Reward History (Raw + Smoothed) ---
        graph_title = self.header_font.render("REWARD HISTORY", True, (255, 255, 255))
        screen.blit(graph_title, (x_offset + 20, y))
        y += 30

        graph_rect = pygame.Rect(x_offset + 20, y, 360, 100)
        pygame.draw.rect(screen, (15, 15, 18), graph_rect)
        pygame.draw.rect(screen, (40, 40, 45), graph_rect, 1)

        if len(history) > 1:
            data = history[-100:]
            h_max, h_min = max(data), min(data)
            range_h = h_max - h_min if h_max != h_min else 1.0
            
            # Raw Data Line (Dimmed)
            points_raw = []
            for i, val in enumerate(data):
                px = x_offset + 20 + (i * (360 / (len(data) - 1)))
                py = (y + 100) - ((val - h_min) / range_h * 80 + 10)
                points_raw.append((int(px), int(py)))
            pygame.draw.lines(screen, (40, 60, 50), False, points_raw, 1)
            
            # Smoothed Trend (EMA)
            smoothed = []
            curr = data[0]
            for val in data:
                curr = curr * 0.9 + val * 0.1
                smoothed.append(curr)
            
            points_smooth = []
            for i, val in enumerate(smoothed):
                px = x_offset + 20 + (i * (360 / (len(data) - 1)))
                py = (y + 100) - ((val - h_min) / range_h * 80 + 10)
                points_smooth.append((int(px), int(py)))
            pygame.draw.lines(screen, (255, 100, 0), False, points_smooth, 3)

import pygame
import numpy as np
from typing import List, Optional


class TeacherEnhancedVisualizer:
    def __init__(self, feature_names: list, width: int = 400):
        self.feature_names = feature_names
        self.width = width
        self.font = pygame.font.SysFont("Arial", 14)
        self.header_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.metric_font = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.alignment_history = []
        self.rolling_rewards = []
        self.alpha = 0.1  # For EMA smoothing

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

    def draw(self, screen, theta, history, alignment_score, x_offset):
        rect = pygame.Rect(x_offset, 0, self.width, screen.get_height())
        pygame.draw.rect(screen, (20, 20, 25), rect)
        pygame.draw.line(screen, (50, 50, 60), (x_offset, 0), (x_offset, screen.get_height()), 2)

        y = 30
        title = self.header_font.render("TEACHER-GUIDED AGENT", True, (0, 255, 200))
        screen.blit(title, (x_offset + 20, y))
        y += 40

        # --- Teacher Alignment (Accuracy) ---
        align_label = self.font.render("TEACHER ALIGNMENT (IMITATION ACCURACY)", True, (150, 150, 160))
        screen.blit(align_label, (x_offset + 20, y))
        y += 25
        
        # Smooth the alignment score for display
        self.alignment_history.append(alignment_score)
        if len(self.alignment_history) > 100: self.alignment_history.pop(0)
        avg_align = np.mean(self.alignment_history) if self.alignment_history else 0
        
        pygame.draw.rect(screen, (40, 40, 45), (x_offset + 20, y, 360, 20))
        pygame.draw.rect(screen, (0, 180, 255), (x_offset + 20, y, int(360 * avg_align), 20))
        
        perc_text = self.metric_font.render(f"{avg_align*100:.1f}%", True, (255, 255, 255))
        screen.blit(perc_text, (x_offset + 320, y - 30))
        y += 40

        # --- Feature Weights ---
        weight_title = self.header_font.render("CORE FEATURE WEIGHTS", True, (255, 255, 255))
        screen.blit(weight_title, (x_offset + 20, y))
        y += 35

        abs_weights = np.abs(theta)
        max_w = np.max(abs_weights) if np.max(abs_weights) > 0 else 1.0
        
        for i, name in enumerate(self.feature_names):
            val = theta[i]
            label = self.font.render(name.upper(), True, (180, 180, 190))
            screen.blit(label, (x_offset + 20, y))
            
            self._draw_gradient_bar(screen, x_offset + 120, y, 200, 12, val, max_w)
            
            val_text = self.font.render(f"{val:+.3f}", True, (220, 220, 230))
            screen.blit(val_text, (x_offset + 330, y - 2))
            y += 28

        y += 30
        # --- Performance Analytics ---
        stats_title = self.header_font.render("PERFORMANCE TRENDS", True, (255, 255, 255))
        screen.blit(stats_title, (x_offset + 20, y))
        y += 35

        # Reward History with Smoothing
        graph_rect = pygame.Rect(x_offset + 20, y, 360, 150)
        pygame.draw.rect(screen, (15, 15, 18), graph_rect)
        pygame.draw.rect(screen, (40, 40, 45), graph_rect, 1)

        if len(history) > 1:
            data = history[-100:]
            h_max = max(data) if max(data) > 0 else 1.0
            h_min = min(data)
            range_h = h_max - h_min if h_max != h_min else 1.0
            
            # Draw Raw Points (Dimmed)
            points_raw = []
            for i, val in enumerate(data):
                px = x_offset + 20 + (i * (360 / (len(data) - 1)))
                py = (y + 150) - ((val - h_min) / range_h * 130 + 10)
                points_raw.append((int(px), int(py)))
            if len(points_raw) > 1:
                pygame.draw.lines(screen, (40, 60, 50), False, points_raw, 1)

            # Draw Smoothed Trend (EMA)
            smoothed = []
            curr = data[0]
            for val in data:
                curr = curr * 0.9 + val * 0.1
                smoothed.append(curr)
                
            points_smooth = []
            for i, val in enumerate(smoothed):
                px = x_offset + 20 + (i * (360 / (len(data) - 1)))
                py = (y + 150) - ((val - h_min) / range_h * 130 + 10)
                points_smooth.append((int(px), int(py)))
            if len(points_smooth) > 1:
                pygame.draw.lines(screen, (0, 255, 120), False, points_smooth, 3)

        y += 170
        # --- Technical Status ---
        status_box = pygame.Rect(x_offset + 20, y, 360, 60)
        pygame.draw.rect(screen, (30, 30, 35), status_box, border_radius=5)
        
        mode_label = self.font.render("TRAINING MODE:", True, (150, 150, 160))
        screen.blit(mode_label, (x_offset + 35, y + 15))
        
        mode_val = self.header_font.render("IMITATION (TEACHER)", True, (255, 200, 0))
        screen.blit(mode_val, (x_offset + 35, y + 30))
        
        # Stability simple indicator
        pygame.draw.circle(screen, (0, 255, 100), (x_offset + 340, y + 30), 8)
        pygame.draw.circle(screen, (0, 100, 50), (x_offset + 340, y + 30), 8, 2)

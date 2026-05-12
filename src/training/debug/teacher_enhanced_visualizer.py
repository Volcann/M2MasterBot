import pygame
import numpy as np


class TeacherEnhancedVisualizer:
    """
    Real-time debug panel for the teacher-guided RLAgent.

    G5 update: teacher_lambda (λ) is now displayed as a live decay bar so you
    can watch the agent transition from imitation → autonomy in real time.
    The TRAINING MODE label flips from "IMITATION (TEACHER)" → "MIXED" →
    "AUTONOMOUS (RL)" as λ crosses threshold values.
    """

    def __init__(self, feature_names: list, width: int = 400):
        self.feature_names = feature_names
        self.width = width
        self.font = pygame.font.SysFont("Arial", 14)
        self.header_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.metric_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.alignment_history = []
        self.lambda_history = []
        self.rolling_rewards = []
        self.alpha = 0.1

    def _draw_gradient_bar(self, screen, x, y, w, h, val, max_val):
        pygame.draw.rect(screen, (40, 40, 45), (x, y, w, h))
        if max_val == 0:
            return
        fill_w = int(abs(val / max_val) * w)
        fill_w = min(fill_w, w)
        if val > 0:
            for i in range(fill_w):
                color = (0, 200 - i * 50 // w, 255)
                pygame.draw.line(screen, color, (x + i, y), (x + i, y + h))
        else:
            for i in range(fill_w):
                color = (255, 80 + i * 40 // w, 80)
                pygame.draw.line(screen, color, (x + i, y), (x + i, y + h))

    def draw(self, screen, theta, history, alignment_score, x_offset,
             teacher_lambda: float = 1.0):
        rect = pygame.Rect(x_offset, 0, self.width, screen.get_height())
        pygame.draw.rect(screen, (20, 20, 25), rect)
        pygame.draw.line(
            screen, (50, 50, 60), (x_offset, 0), (x_offset, screen.get_height()), 2
        )
        y = 30

        title = self.header_font.render("TEACHER-GUIDED AGENT", True, (0, 255, 200))
        screen.blit(title, (x_offset + 20, y))
        y += 40

        # ── Teacher λ decay bar (G5) ──────────────────────────────────────
        lam_label = self.font.render(
            f"TEACHER INFLUENCE (λ): {teacher_lambda:.4f}", True, (150, 150, 160)
        )
        screen.blit(lam_label, (x_offset + 20, y))
        y += 20
        pygame.draw.rect(screen, (40, 40, 45), (x_offset + 20, y, 360, 12))
        # Colour gradient: green (full teacher) → orange (mixed) → red (autonomous)
        lam_r = int(255 * (1.0 - teacher_lambda))
        lam_g = int(255 * teacher_lambda)
        pygame.draw.rect(
            screen,
            (lam_r, lam_g, 60),
            (x_offset + 20, y, int(360 * teacher_lambda), 12),
        )
        y += 22

        self.lambda_history.append(teacher_lambda)
        if len(self.lambda_history) > 200:
            self.lambda_history.pop(0)

        # λ sparkline
        spark_rect = pygame.Rect(x_offset + 20, y, 360, 40)
        pygame.draw.rect(screen, (15, 15, 18), spark_rect)
        pygame.draw.rect(screen, (40, 40, 45), spark_rect, 1)
        if len(self.lambda_history) > 1:
            data = self.lambda_history
            pts = []
            for i, v in enumerate(data):
                px = x_offset + 20 + i * (360 / max(len(data) - 1, 1))
                py = y + 40 - int(v * 36) - 2
                pts.append((int(px), int(py)))
            pygame.draw.lines(screen, (0, 200, 120), False, pts, 2)
        y += 50

        # ── Alignment bar ─────────────────────────────────────────────────
        align_label = self.font.render(
            "TEACHER ALIGNMENT (IMITATION ACCURACY)", True, (150, 150, 160)
        )
        screen.blit(align_label, (x_offset + 20, y))
        y += 20
        self.alignment_history.append(alignment_score)
        if len(self.alignment_history) > 100:
            self.alignment_history.pop(0)
        avg_align = np.mean(self.alignment_history) if self.alignment_history else 0
        pygame.draw.rect(screen, (40, 40, 45), (x_offset + 20, y, 360, 16))
        pygame.draw.rect(
            screen, (0, 180, 255), (x_offset + 20, y, int(360 * avg_align), 16)
        )
        perc_text = self.metric_font.render(
            f"{avg_align * 100:.1f}%", True, (255, 255, 255)
        )
        screen.blit(perc_text, (x_offset + 310, y - 28))
        y += 30

        # ── Feature weights ───────────────────────────────────────────────
        weight_title = self.header_font.render(
            "CORE FEATURE WEIGHTS", True, (255, 255, 255)
        )
        screen.blit(weight_title, (x_offset + 20, y))
        y += 30
        abs_weights = np.abs(theta)
        max_w = np.max(abs_weights) if np.max(abs_weights) > 0 else 1.0
        for i, name in enumerate(self.feature_names):
            val = theta[i]
            label = self.font.render(name.upper(), True, (180, 180, 190))
            screen.blit(label, (x_offset + 20, y))
            self._draw_gradient_bar(screen, x_offset + 120, y, 200, 12, val, max_w)
            val_text = self.font.render(f"{val:+.3f}", True, (220, 220, 230))
            screen.blit(val_text, (x_offset + 330, y - 2))
            y += 26
        y += 15

        # ── Performance trend ─────────────────────────────────────────────
        stats_title = self.header_font.render(
            "PERFORMANCE TRENDS", True, (255, 255, 255)
        )
        screen.blit(stats_title, (x_offset + 20, y))
        y += 28
        graph_rect = pygame.Rect(x_offset + 20, y, 360, 120)
        pygame.draw.rect(screen, (15, 15, 18), graph_rect)
        pygame.draw.rect(screen, (40, 40, 45), graph_rect, 1)
        if len(history) > 1:
            data = history[-100:]
            h_max = max(data) if max(data) > 0 else 1.0
            h_min = min(data)
            range_h = h_max - h_min if h_max != h_min else 1.0
            points_raw = []
            for i, val in enumerate(data):
                px = x_offset + 20 + i * (360 / max(len(data) - 1, 1))
                py = y + 120 - ((val - h_min) / range_h * 100 + 10)
                points_raw.append((int(px), int(py)))
            if len(points_raw) > 1:
                pygame.draw.lines(screen, (40, 60, 50), False, points_raw, 1)
            smoothed, curr = [], data[0]
            for val in data:
                curr = curr * 0.9 + val * 0.1
                smoothed.append(curr)
            pts_s = []
            for i, val in enumerate(smoothed):
                px = x_offset + 20 + i * (360 / max(len(smoothed) - 1, 1))
                py = y + 120 - ((val - h_min) / range_h * 100 + 10)
                pts_s.append((int(px), int(py)))
            if len(pts_s) > 1:
                pygame.draw.lines(screen, (0, 255, 120), False, pts_s, 3)
        y += 135

        # ── Training mode label (reflects current λ) ──────────────────────
        status_box = pygame.Rect(x_offset + 20, y, 360, 52)
        pygame.draw.rect(screen, (30, 30, 35), status_box, border_radius=5)
        mode_label = self.font.render("TRAINING MODE:", True, (150, 150, 160))
        screen.blit(mode_label, (x_offset + 35, y + 8))

        if teacher_lambda > 0.7:
            mode_str, mode_color, dot_color = "IMITATION (TEACHER)", (255, 200, 0), (255, 200, 0)
        elif teacher_lambda > 0.2:
            mode_str, mode_color, dot_color = "MIXED POLICY", (255, 140, 0), (255, 140, 0)
        else:
            mode_str, mode_color, dot_color = "AUTONOMOUS (RL)", (0, 255, 100), (0, 255, 100)

        mode_val = self.header_font.render(mode_str, True, mode_color)
        screen.blit(mode_val, (x_offset + 35, y + 26))
        pygame.draw.circle(screen, dot_color, (x_offset + 350, y + 34), 7)
        pygame.draw.circle(screen, (30, 30, 35), (x_offset + 350, y + 34), 7, 2)

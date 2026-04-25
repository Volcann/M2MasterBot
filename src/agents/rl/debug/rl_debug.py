import numpy as np
from agents.heuristic.debug.debug import Debugger, GOLD, ACCENT


class RLDebugger(Debugger):
    def __init__(self, feature_keys):
        super().__init__(feature_keys)
        self.fig.text(
            0.5,
            0.975,
            "RL  AGENT  DEBUG  PANEL",
            ha="center",
            va="top",
            color=ACCENT,
            fontsize=16,
            fontweight="bold",
            fontstyle="italic",
        )

    def update_rl(self, column, contributions, q_score, move_summaries, weights):
        self._current_weights = weights
        self.update(column, contributions, q_score)
        self.draw_summary(move_summaries, column)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def _redraw_radar(self, contributions):
        if not hasattr(self, "_current_weights"):
            return super()._redraw_radar(contributions)
        weights = self._current_weights
        raw = [abs(w) for w in weights]
        mx = max(raw) or 1.0
        norm = [v / mx for v in raw]
        norm_closed = norm + norm[:1]
        self._radar_line.set_data(self._radar_angles, norm_closed)
        xy = np.column_stack([self._radar_angles_np, np.array(norm_closed)])
        self._radar_fill.set_xy(xy)
        angles_arr = np.array(self._radar_angles[:-1])
        self._radar_dots.set_offsets(np.column_stack([angles_arr, np.array(norm)]))
        self.ax_radar.set_title(
            "LEARNED  WEIGHTS  (THETA)",
            color=GOLD,
            fontsize=11,
            fontweight="bold",
            pad=20,
        )

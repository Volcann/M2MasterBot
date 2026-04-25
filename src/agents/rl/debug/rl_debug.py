import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from agents.heuristic.debug.debug import Debugger, FEATURE_COLORS, PANEL, BORDER, GOLD, ACCENT, TEXT, DIM, GREEN


class RLDebugger(Debugger):
    def __init__(self, feature_keys):
        super().__init__(feature_keys)
        # We can add RL-specific tweaks here if needed
        self.fig.text(
            0.5, 0.975,
            'RL  AGENT  DEBUG  PANEL',
            ha='center', va='top',
            color=ACCENT, fontsize=16,
            fontweight='bold',
            fontstyle='italic'
        )

    def update_rl(self, column, contributions, q_score, move_summaries, weights):
        """
        Specialized update for RL that also knows about the current weights (theta).
        """
        self._current_weights = weights # Store for _redraw_radar override
        self.update(column, contributions, q_score)
        self.draw_summary(move_summaries, column)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def _redraw_radar(self, contributions):
        """
        Override to show the actual learned theta weights in the radar chart
        instead of the per-move feature distribution.
        """
        if not hasattr(self, '_current_weights'):
            return super()._redraw_radar(contributions)
            
        weights = self._current_weights
        raw = [abs(w) for w in weights]
        mx = max(raw) or 1.0
        norm = [v / mx for v in raw]
        norm_closed = norm + norm[:1]

        # Update line in-place
        self._radar_line.set_data(self._radar_angles, norm_closed)

        # Update fill polygon in-place
        xy = np.column_stack([self._radar_angles_np, np.array(norm_closed)])
        self._radar_fill.set_xy(xy)

        # Update dot positions
        angles_arr = np.array(self._radar_angles[:-1])
        self._radar_dots.set_offsets(
            np.column_stack([angles_arr, np.array(norm)])
        )
        
        self.ax_radar.set_title(
            'LEARNED  WEIGHTS  (THETA)', color=GOLD,
            fontsize=11, fontweight='bold', pad=20
        )

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import deque

matplotlib.rcParams["font.family"] = "monospace"
BG = "#080b12"
PANEL = "#0f1420"
BORDER = "#1e2a40"
ACCENT = "#00d4ff"
GREEN = "#00e676"
GOLD = "#ffd740"
RED = "#ff5252"
TEXT = "#e0e8ff"
DIM = "#4a5568"
FEATURE_COLORS = ["#ff6b6b", "#ffa94d", "#ffe066", "#69db7c", "#4dabf7", "#da77f2"]


class Debugger:
    def __init__(self, feature_keys):
        self.feature_keys = feature_keys
        self.n = len(feature_keys)
        self._history = {k: deque(maxlen=30) for k in feature_keys}
        self._hscore_history = deque(maxlen=30)
        self._last_contributions = {k: 0.0 for k in feature_keys}
        self._best_col = None
        self._move_summaries = []
        self._draw_counter = 0
        plt.ion()
        self.fig = plt.figure(figsize=(20, 11), facecolor=BG)
        self.fig.patch.set_facecolor(BG)
        try:
            mgr = plt.get_current_fig_manager()
            mgr.full_screen_toggle()
        except Exception:
            try:
                mgr.window.showMaximized()
            except Exception:
                pass
        gs = gridspec.GridSpec(
            3,
            2,
            figure=self.fig,
            height_ratios=[1, 1, 1],
            width_ratios=[1.1, 1.0],
            hspace=0.52,
            wspace=0.4,
            left=0.06,
            right=0.97,
            top=0.91,
            bottom=0.05,
        )
        self.ax_radar = self.fig.add_subplot(gs[:, 0], polar=True)
        self.ax_bars = self.fig.add_subplot(gs[0, 1])
        self.ax_history = self.fig.add_subplot(gs[1, 1])
        self.ax_table = self.fig.add_subplot(gs[2, 1])
        self._style_all_axes()
        self._init_bars()
        self._init_radar()
        self._init_history()
        self._init_table()
        self.fig.text(
            0.5,
            0.975,
            "HEURISTIC  DEBUG  PANEL",
            ha="center",
            va="top",
            color=ACCENT,
            fontsize=16,
            fontweight="bold",
            fontstyle="italic",
        )
        plt.show(block=False)
        self.fig.canvas.draw()

    def _style_ax(self, ax):
        ax.set_facecolor(PANEL)
        for spine in ax.spines.values():
            spine.set_color(BORDER)
            spine.set_linewidth(1.2)
        ax.tick_params(colors=DIM, labelsize=8)
        ax.xaxis.label.set_color(DIM)
        ax.yaxis.label.set_color(DIM)

    def _style_all_axes(self):
        for ax in [self.ax_bars, self.ax_history, self.ax_table]:
            self._style_ax(ax)
        self.ax_radar.set_facecolor(PANEL)
        self.ax_radar.tick_params(colors=DIM, labelsize=7)
        for spine in self.ax_radar.spines.values():
            spine.set_color(BORDER)

    def _init_bars(self):
        ax = self.ax_bars
        self._bars = ax.barh(
            self.feature_keys,
            [0.0] * self.n,
            color=FEATURE_COLORS[: self.n],
            edgecolor="none",
            height=0.55,
        )
        self._bar_labels = []
        for i, key in enumerate(self.feature_keys):
            lbl = ax.text(
                0,
                i,
                "",
                color=TEXT,
                va="center",
                ha="left",
                fontsize=9,
                fontweight="bold",
            )
            self._bar_labels.append(lbl)
        ax.axvline(0, color=BORDER, linewidth=1.0)
        ax.set_xscale("symlog", linthresh=0.05)
        ax.xaxis.grid(True, linestyle=":", alpha=0.2, color=DIM, which="both")
        ax.set_title(
            "FEATURE  IMPACT  PER  MOVE",
            color=ACCENT,
            fontsize=11,
            fontweight="bold",
            pad=10,
        )
        ax.tick_params(axis="y", colors=TEXT, labelsize=10)

    def _init_radar(self):
        ax = self.ax_radar
        angles = np.linspace(0, 2 * np.pi, self.n, endpoint=False).tolist()
        angles += angles[:1]
        self._radar_angles = angles
        self._radar_angles_np = np.array(angles)
        (self._radar_line,) = ax.plot(
            angles,
            [0.0] * (self.n + 1),
            color=ACCENT,
            linewidth=2.2,
            linestyle="solid",
            zorder=3,
        )
        (self._radar_fill,) = ax.fill(
            angles, [0.0] * (self.n + 1), color=ACCENT, alpha=0.18, zorder=2
        )
        self._radar_dots = ax.scatter(
            angles[:-1],
            [0.0] * self.n,
            c=FEATURE_COLORS[: self.n],
            s=55,
            zorder=4,
            edgecolors="none",
        )
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.feature_keys, fontsize=13, fontweight="bold")
        for label, c in zip(ax.get_xticklabels(), FEATURE_COLORS[: self.n]):
            label.set_color(c)
        ax.set_yticklabels([])
        ax.set_ylim(0, 1)
        ax.set_title("DISTRIBUTION", color=GOLD, fontsize=11, fontweight="bold", pad=20)
        ax.grid(color=BORDER, linewidth=0.8)

    def _init_history(self):
        ax = self.ax_history
        self._history_lines = {}
        for i, key in enumerate(self.feature_keys):
            (line,) = ax.plot(
                [],
                [],
                label=key,
                color=FEATURE_COLORS[i % len(FEATURE_COLORS)],
                linewidth=1.4,
                alpha=0.85,
            )
            self._history_lines[key] = line
        (self._hscore_line,) = ax.plot(
            [],
            [],
            label="h-score",
            color=GOLD,
            linewidth=2.5,
            linestyle="--",
            alpha=0.9,
        )
        ax.set_title(
            "CONTRIBUTION  HISTORY", color=ACCENT, fontsize=9, fontweight="bold", pad=10
        )
        ax.legend(
            loc="upper left",
            fontsize=9,
            facecolor=PANEL,
            edgecolor=BORDER,
            labelcolor=TEXT,
            ncol=2,
            borderpad=0.7,
            handlelength=1.8,
            handletextpad=0.6,
            labelspacing=0.5,
        )
        ax.tick_params(colors=DIM, labelsize=8)
        ax.xaxis.grid(True, linestyle=":", alpha=0.2, color=DIM)
        ax.yaxis.grid(True, linestyle=":", alpha=0.2, color=DIM)

    def _init_table(self):
        self.ax_table.axis("off")

    def update(self, column, contributions, total_heuristic):
        self._last_contributions = contributions
        self._best_col = None
        self._draw_counter += 1
        for key in self.feature_keys:
            self._history[key].append(contributions.get(key, 0.0))
        self._hscore_history.append(total_heuristic)
        self._redraw_bars(column, contributions, total_heuristic)
        self._redraw_radar(contributions)
        self._redraw_history()
        if self._draw_counter % 3 == 0:
            self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def _redraw_bars(self, column, contributions, total_heuristic):
        ax = self.ax_bars
        values = [contributions.get(k, 0.0) for k in self.feature_keys]
        total_abs = sum((abs(v) for v in values)) or 1.0
        max_abs = max((abs(v) for v in values)) if values else 1.0
        for i, (bar, key) in enumerate(zip(self._bars, self.feature_keys)):
            val = contributions.get(key, 0.0)
            bar.set_width(val)
            bar.set_alpha(0.9 if val != 0 else 0.25)
            pct = abs(val) / total_abs * 100
            offset = max_abs * 0.08
            sign = 1 if val >= 0 else -1
            self._bar_labels[i].set_text(f"  {val:+.3f}  ({pct:.1f}%)")
            self._bar_labels[i].set_x(val + sign * offset)
            self._bar_labels[i].set_ha("left" if val >= 0 else "right")
        xlim_lo = min(min(values) * 1.8, -0.15) if values else -1
        xlim_hi = max(max(values) * 2.5, 0.5) if values else 1
        ax.set_xlim(xlim_lo, xlim_hi)
        ax.set_title(
            f"COL {column}   ·   H-SCORE  {total_heuristic:+.4f}",
            color=ACCENT,
            fontsize=12,
            fontweight="bold",
            pad=10,
        )

    def _redraw_radar(self, contributions):
        raw = [abs(contributions.get(k, 0.0)) for k in self.feature_keys]
        mx = max(raw) or 1.0
        norm = [v / mx for v in raw]
        norm_closed = norm + norm[:1]
        self._radar_line.set_data(self._radar_angles, norm_closed)
        xy = np.column_stack([self._radar_angles_np, np.array(norm_closed)])
        self._radar_fill.set_xy(xy)
        angles_arr = np.array(self._radar_angles[:-1])
        self._radar_dots.set_offsets(np.column_stack([angles_arr, np.array(norm)]))

    def _redraw_history(self):
        ax = self.ax_history
        for key, line in self._history_lines.items():
            data = list(self._history[key])
            line.set_data(range(len(data)), data)
        hs = list(self._hscore_history)
        self._hscore_line.set_data(range(len(hs)), hs)
        if self._draw_counter % 5 == 0:
            ax.relim()
            ax.autoscale_view()

    def draw_summary(self, summary_data, best_column):
        self._best_col = best_column
        self._move_summaries = summary_data
        ax = self.ax_table
        ax.cla()
        ax.axis("off")
        ax.set_facecolor(PANEL)
        if not summary_data:
            return
        headers = ["COL", "SCORE GAIN", "H-SCORE", "MERGES", "RANK"]
        sorted_data = sorted(summary_data, key=lambda d: d["h_score"], reverse=True)
        rank_map = {d["col"]: i + 1 for i, d in enumerate(sorted_data)}
        rows = []
        row_colors = []
        for d in summary_data:
            rank = rank_map[d["col"]]
            rows.append(
                [
                    str(d["col"]),
                    str(d["score"]),
                    f"{d['h_score']:.4f}",
                    str(d["merges"]),
                    f"#{rank}",
                ]
            )
            if d["col"] == best_column:
                row_colors.append(
                    ["#003300", "#004400", "#004400", "#003300", "#004400"]
                )
            elif rank == 1:
                row_colors.append([PANEL] * 5)
            else:
                row_colors.append(["#0d1117"] * 5)
        col_widths = [0.08, 0.18, 0.18, 0.14, 0.1]
        table = ax.table(
            cellText=rows,
            colLabels=headers,
            cellColours=row_colors,
            colWidths=col_widths,
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.2)
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor(BORDER)
            cell.set_linewidth(0.8)
            if row == 0:
                cell.set_facecolor("#111827")
                cell.set_text_props(color=ACCENT, fontweight="bold", fontsize=10)
            else:
                d = summary_data[row - 1]
                if d["col"] == best_column:
                    cell.get_text().set_color(GREEN)
                    cell.get_text().set_fontweight("bold")
                else:
                    cell.get_text().set_color(TEXT)
        ax.set_title(
            f"MOVE  SUMMARY   ·   WINNER → COLUMN  {best_column}",
            color=GREEN,
            fontsize=11,
            fontweight="bold",
            pad=8,
        )
        self.ax_bars.set_title(
            f"COL {best_column}  CHOSEN  ✓   H-SCORE  {summary_data[best_column]['h_score']:+.4f}"
            if best_column < len(summary_data)
            else f"WINNER: COLUMN {best_column}",
            color=GREEN,
            fontsize=12,
            fontweight="bold",
            pad=10,
        )
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

import matplotlib.pyplot as plt
import numpy as np


class Debugger:
    def __init__(self, feature_keys):
        plt.ion()
        self.figure = plt.figure(figsize=(7, 5))
        grid_spec = self.figure.add_gridspec(2, 1, height_ratios=[1.3, 1])

        self.ax_bars = self.figure.add_subplot(grid_spec[0])
        self.ax_table = self.figure.add_subplot(grid_spec[1])

        self.feature_keys = feature_keys
        self.colors = plt.cm.plasma(np.linspace(0.4, 0.8, len(feature_keys)))

        self.bg_color = '#0f0f0f'
        self.accent_color = '#00e5ff'
        self.figure.patch.set_facecolor(self.bg_color)
        self.ax_bars.set_facecolor(self.bg_color)
        self.ax_table.set_facecolor(self.bg_color)

        self.bars = self.ax_bars.barh(
            self.feature_keys,
            [0] * len(feature_keys),
            color=self.colors
        )

        self.labels = [
            self.ax_bars.text(
                0, i, '', color='white', va='center',
                fontweight='bold', fontsize=9
            )
            for i in range(len(feature_keys))
        ]

        self.ax_bars.tick_params(colors='white', labelsize=8)
        self.ax_bars.set_xscale('symlog', linthresh=0.1)
        self.ax_bars.spines['bottom'].set_color('#555')
        self.ax_bars.xaxis.grid(True, linestyle=':', alpha=0.3, which='both')

        self.ax_table.axis('off')
        plt.tight_layout(pad=2.0)
        plt.show(block=False)

    def update(self, column, contributions, total_heuristic):
        self.ax_bars.set_title(
            f"COL {column} | H-SCORE: {total_heuristic:.3f}",
            color=self.accent_color,
            fontweight='bold',
            fontsize=10
        )

        values = list(contributions.values())
        max_magnitude = max([abs(v) for v in values]) if values else 1
        total_abs_sum = sum([abs(v) for v in values]) or 1

        for i, key in enumerate(self.feature_keys):
            val = contributions.get(key, 0)
            percentage = (abs(val) / total_abs_sum) * 100
            self.bars[i].set_width(val)

            offset = max_magnitude * 0.15
            self.labels[i].set_text(f" {val:.2f} ({percentage:.1f}%)")
            self.labels[i].set_x(val + offset if val >= 0 else val - (offset * 4))

        self.ax_bars.set_xlim(
            min(min(values) * 2, -0.2),
            max(max(values) * 3, 1.2)
        )

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def draw_summary(self, summary_data, best_column):
        self.ax_table.clear()
        self.ax_table.axis('off')

        headers = ["COL", "GAIN", "HEURISTIC", "MERGES"]
        rows = [
            [d['col'], d['score'], f"{d['h_score']:.3f}", d['merges']]
            for d in summary_data
        ]

        row_colors = [
            ['#1b5e20' if d['col'] == best_column else '#252525'] * 4
            for d in summary_data
        ]

        table = self.ax_table.table(
            cellText=rows,
            colLabels=headers,
            cellColours=row_colors,
            loc='center',
            cellLoc='center'
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.3)

        for (row, col), cell in table.get_celld().items():
            cell.get_text().set_color('white')
            cell.set_edgecolor('#333')
            if row == 0:
                cell.set_facecolor('#444')
                cell.set_text_props(fontweight='bold', color=self.accent_color)

        self.ax_bars.set_title(
            f"WINNER: COLUMN {best_column}",
            color='#4caf50',
            fontweight='bold',
            fontsize=12
        )
        self.figure.canvas.draw()

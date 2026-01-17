# M2 Block 🎮

**M2 Block** is a modern twist on the classic 2048 puzzle game. Place tiles strategically to merge them, score points, and reach the highest tile! The game features a smooth Pygame interface, animated tile merges, drop effects, and an intelligent AI bot that can play for you.

---

## 🎯 Features

* **Classic Gameplay**: Drop tiles in columns to merge numbers. Combine same values to increase your score.
* **AI Bot**: `GameBot` calculates optimal moves based on heuristics like merges, empty spaces, smoothness, monotonicity, and corner strategy.
* **Dynamic UI**:

  * Animated merges and tile drops
  * Glowing tiles with smooth easing effects
  * Responsive fullscreen scaling
* **Score Tracking**: Keep track of your best score across sessions.
* **Next Tile Preview**: Always see your next tile to plan your moves.
* **Keyboard & Mouse Input**: Play using `R` to restart, `0-9` to drop in a column, or click on the grid.

---

## 🎨 Visuals

* Smooth glowing tiles with color gradients based on value.
* Pulse animation when tiles merge.
* Real-time feedback for merges and tile drops.
* High-quality fonts and responsive layout for any window size.

---

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/m2-block.git
cd m2-block
```

2. Install dependencies (requires Python ≥ 3.10):

```bash
pip install -r requirements.txt
```

3. Run the game:

```bash
python main.py
```

---

## 🕹 How to Play

* **Mouse**: Hover over a column to highlight, click to drop the tile.
* **Keyboard**:

  * `0-9` → Drop tile in the corresponding column
  * `R` → Restart the game
* **Goal**: Merge tiles to create higher values. Strategic placement maximizes your score.

---

## 🤖 AI Bot

The game includes a `GameBot` class that can simulate moves and suggest the best column to play. The bot evaluates:

* Number of empty spaces
* Potential merges
* Smoothness of the board
* Tile monotonicity
* Corner strategy (keep the largest tile in a corner)

Example usage:

```python
from game_logic.game_bot import GameBot

bot = GameBot()
best_column = bot.solve(matrix, next_tile_value)
```

---

## 🛠 Tech Stack

* **Python 3.10+**
* **Pygame** for graphics and animations
* Modular design for AI and game logic separation

---

## 🎉 Credits

* Developed by **volcani**
* Inspired by **2048** and modern puzzle games

---

## 📄 License

This project is open-source under the **MIT License**.

---

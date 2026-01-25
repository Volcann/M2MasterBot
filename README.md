# M2 Merge Block Bot
![M2 Merge Block Game](https://github.com/Volcann/M2MasterBot/blob/92beb45387ec467a4a7d8915338a2f26dbbdc424/assets/image.png)

*Screenshot of the M2 Merge Block Game in action*

This repository contains the logic and AI bot for the **M2 Merge Block** game. The bot uses **heuristics** to decide the best moves and can be extended for **reinforcement learning** in the future.

---

## 1. Heuristics Used (Current Approach)

The bot evaluates the board using a set of **weighted features** to choose the best move. These features capture the strategy and dynamics of the game:

| Feature | Description |
|---------|-------------|
| **Score** | Expected gain from merging blocks in this move. |
| **Empty** | Number of empty cells after the move (more space → more options). |
| **Merge** | Number of successful merges in the move. |
| **Monotonicity (Mono)** | How consistently values increase or decrease across rows/columns. |
| **Smoothness** | Measures how “smooth” the board is (avoids scattered high-value tiles). |
| **Corner Bonus** | Encourages keeping the highest-value tile in a corner. |

**How it works:**
1. The bot simulates a move in each column.
2. Computes the feature values for that move.
3. Applies predefined **weights** to each feature to calculate a **heuristic score**.
4. Chooses the column with the **highest heuristic score**.
5. Optionally updates weights if reinforcement learning is applied later.

> 🔹 This ensures deterministic, stable, and predictable AI behavior.

---

## 2. Reinforcement Learning (To-Do / Future Work)

The current bot is **heuristic-based**, but it can be extended with **reinforcement learning (RL)** to improve its strategy automatically:

**Ideas:**
- **State:** The current board matrix.
- **Action:** Place the next value in one of the columns.
- **Reward:** 
  - Positive: Merges, score gain, creating empty cells.
  - Negative: Losing move, full column, bad board arrangement.
- **Approach:**
  - Use Q-Learning or Deep Q-Network (DQN) to learn optimal moves over time.
  - Combine **heuristics as initial rewards** to guide the early training.
  - Optionally, implement **self-play** for faster learning.

**Goals:**
- The bot can **adapt** to different play styles.
- Improve long-term performance beyond heuristic limitations.
- Eventually **discover new strategies** that humans may not think of.

---

## 3. Setup & Run (Heuristic Bot)

**Step 1:** Create and activate a virtual environment  
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
````

**Step 2:** Install dependencies

```bash
pip install -r requirements.txt
```

**Step 3:** Run the heuristic bot

```bash
python run_bot.py
```

> The bot will play the game automatically using the heuristic strategy.

---

## 4. Setup & Run (Play Yourself)

After setting up the virtual environment and installing requirements, you can play the game manually:

```bash
python main.py
```

* Use **mouse** or **number keys (0–4)** to drop the next block in the desired column.
* Press **R** to restart the game anytime.

---

### 📝 Notes
- The bot is fully deterministic: same board → same move.
- Can be integrated with a GUI (like the `GameUI` class) to test and visualize performance.
- Designed for educational purposes and AI research in simple strategy games.

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

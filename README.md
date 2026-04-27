# M2 Merge Block Bot

![M2 Merge Block Game](https://github.com/Volcann/M2MasterBot/blob/92beb45387ec467a4a7d8915338a2f26dbbdc424/assets/image.png)

A comprehensive Reinforcement Learning (RL) and Heuristic-based AI framework for the **M2 Merge Block** game. This project serves as both a high-performance game bot and a research platform for observing RL dynamics — including real-time weight visualization, adaptive learning, and catastrophic failure cycles.

---

## 🏗️ Core Architecture

The project utilizes a modular, decoupled architecture to ensure that game physics, agent intelligence, and the visual interface remain isolated and interchangeable.

* **Game Engine (`src/core/`):** Provides deterministic simulation. Bots can "look ahead" using `simulate_move` to evaluate potential board states before committing.
* **Feature Engineering:** Board states are translated into a six-dimensional vector. High-level agents use **feature normalization** to prevent raw score values from drowning out strategic features like smoothness.
* **UI & Visualization:** A premium Pygame implementation that provides a "real-time MRI" of the agent's decision-making process.

---

## 🛠️ The Feature Set

Every agent evaluates the board using these six semantic features. In the **BasicBot** and **RLAgent**, these are scaled mathematically for stability:

| Feature | Description | Mathematical Context |
| :--- | :--- | :--- |
| **Score** | Immediate points gained. | Logarithmic scaling: $log_2(x+1)$ |
| **Empty Cells** | Number of open slots. | Soft-normalized (Crucial for survival) |
| **Merge Count** | Distinct merges triggered. | Linear reward multiplier |
| **Monotonicity** | Directional consistency. | Measures downward value gradients |
| **Smoothness** | Adjacency similarity. | Inverse of variance $\sigma^2$ between tiles |
| **Corner Bonus** | Strategic anchoring. | Reward for highest tile at $[0,0]$ |

---

## 🤖 Agent Hierarchy & Learning Strategy

The framework implements a tiered approach to AI, allowing you to observe the evolution from static logic to self-taught mastery.

### 🔴 Heuristic Baselines
* **FixedLinearBot:** Uses static, hand-tuned weights. It is the control group for performance benchmarks.
* **AdaptiveLinearBot:** Starts with uniform weights and uses a **Reward-Weighted Gradient** to adjust priorities after every move:
    $$W_{t+1} = W_t + \alpha (r - \bar{r}) \nabla f$$
    *(Where $\alpha$ is the learning rate and $f$ is the feature vector)*.

### 🟢 The "Teacher" (`BasicBot`)
Our most sophisticated heuristic agent. By utilizing `soft_norm` and `tanh` activations, it maintains a balanced strategy that doesn't collapse as scores reach the thousands. It serves as the primary supervisor for RL training.

### 🔵 Reinforcement Learning (`RLAgent`)
* **Self-Taught (NoTeacher):** Pure Q-learning from scratch. Often experiences **Catastrophic Failure** cycles—forgetting general survival while over-optimizing for specific high-value merges.
* **Imitation Learning (With Teacher):** The agent begins by mimicking the `BasicBot`. As it plateaus, the teacher's influence is decayed, allowing the RL agent to discover superhuman strategies the human-designed heuristic missed.

---

## 📊 Premium Visualization System

Designed for real-time AI research, the debug panel offers high-fidelity insights:

* **Weight Sparklines:** Dynamic line graphs showing how the bot's priorities (e.g., "Empty Cells" vs. "Corner Bonus") shift during gameplay.
* **Action-Space Heatmap:** Simultaneously visualizes the heuristic score for every column, revealing the "confidence" behind a chosen move.
* **Metric Overlay:** Live tracking of **Epsilon** (exploration rate), **Cumulative Reward**, and **Merge Efficiency**.
* **Micro-Animations:** Shard-based particle effects and "quintic-easing" for tile movements.

---

## 🚀 Key Features

### 🧠 Multi-Strategy AI
- **Fixed Heuristic** — A simple baseline with hardcoded weights. No learning, fully deterministic.
- **Adaptive Heuristic** — Starts from scratch and adjusts its own weights as it plays.
- **Tuned Linear Bot** — Pre-tuned weights that still adapt during a game. The best of both worlds.
- **Normalized Heuristic (BasicBot)** — Balanced, stable features that stay consistent across every board state.
- **RL without Teacher** — Pure Q-learning from random weights. Slow to learn, but entirely self-taught.
- **RL with Teacher** — An agent guided by the heuristic bot during training. Fastest to converge, highest ceiling.

### 📊 Real-Time Visualization
- **Weight Sparklines** — Live tracking of model weight changes while the bot plays.
- **Performance Metrics** — Real-time scores, move counts, and merge stats.
- **Debug Mode** — Per-column heuristic breakdowns so you can see exactly why the bot chose a move.

---

## 🧩 How Each Bot Works

Here's a breakdown of all six bots, from simplest to most sophisticated:

---

### 1. 🔴 `FixedLinearBot` — Least Accurate

The most basic bot in the lineup. It uses a fixed set of hand-picked weights that never change — no matter how the game unfolds.

- Weights like `empty_cells = 100` and `corner_bonus = 200` are set once at startup
- Because the features aren't normalized, raw score values (which can be in the thousands) completely dominate smaller features like the corner bonus (0.0–1.0)
- It will always make the same decision given the same board — no learning, no adaptation
- **Best used as:** a reproducible baseline to compare other bots against

---

### 2. 🟠 `AdaptiveLinearBot` — Low-Medium Accuracy

This bot starts with zero prior knowledge — all six weights begin at an equal `1/6` — and tries to learn what matters as it plays.

- Weight updates happen after every move using a reward-weighted gradient
- The problem is that early in the game, the bot is essentially guessing. It has to play badly before it can play well
- In a single game session there usually isn't enough time for the weights to converge to something meaningful
- **Best used as:** an experiment — run it for many games in a row and watch it slowly improve

---

### 3. 🟡 `LinearBot` — Medium Accuracy

Think of this as the `AdaptiveLinearBot` but with a head start. Instead of equal weights, it begins with a pre-tuned set (e.g. `empty_cells = 100`, `corner_bonus = 200`) so its early moves are already reasonable.

- It still adapts its weights during play, combining prior intuition with live feedback
- Avoids the "blind early game" problem that the Adaptive bot suffers from
- The raw (un-normalized) features are still a weakness — some values naturally dominate others
- **Best used as:** a decent all-around bot when you don't want to run RL training

---

### 4. 🟢 `BasicBot` — Medium-High Accuracy

This is where things get more principled. The `BasicBot` (formerly called `HeuristicBot`) uses **feature normalization** — every input to the weight calculation is squashed into a 0–1 range before being used.

- Uses `soft_norm`, `tanh`, and log-based normalization so no single feature can drown out the others
- Weights are kept balanced (they always sum to 1.0), which makes updates stable and meaningful
- The bot behaves more consistently across different board states compared to the Linear variants
- It's also the **teacher** used to guide RL training — which tells you something about how reliable it is
- **Best used as:** your go-to heuristic bot if you just want strong, consistent play

---

### 5. 🔵 `NoTeacherAgent` — Variable (Depends on Training)

This is a pure Reinforcement Learning agent — no heuristic guidance, just trial and error. It starts with random weights and learns purely from the rewards it receives during play.

- Uses epsilon-greedy exploration: it occasionally picks random moves to discover new strategies
- Untrained, it plays like a random bot. After many episodes, it can become quite good
- Convergence is slow because there's no supervision — the agent has to figure everything out on its own
- The more episodes you train it for, the stronger it gets
- **Best used as:** a research tool to observe how RL works from scratch, or when you have time to train it properly

---

### 6. 🏆 `RLAgent` (with Teacher) — Most Accurate (when trained)

The strongest bot when properly trained. During training, the `BasicBot` acts as a teacher — the RL agent learns to imitate it using policy gradient updates, then gradually diverges toward its own optimal strategy.

- Starts with strong intuitions borrowed from the heuristic teacher
- Because it begins from a good place, it converges much faster than the no-teacher variant
- After training, it often outperforms the `BasicBot` because it can discover patterns the heuristic can't
- Inference uses `epsilon = 0` — fully deterministic, best-known action every move
- **Best used as:** your final, production-ready bot after a proper training run with `rl_agent.json`

---

## 🏁 Accuracy Ranking

```
FixedLinear  <  AdaptiveLinear  <  LinearBot  <  BasicBot  <  NoTeacher RL  <  Teacher RL
```

> **Note:** The Teacher RL wins — but only when it's been trained. A fresh, untrained RL agent will lose to even the `FixedLinearBot`. If you're unsure, just run the `BasicBot`. It's reliable out of the box.

---

## 🏃 Getting Started

### Prerequisites
- Python 3.10+
- Pygame
- NumPy

### Installation

```bash
# Clone the repo
git clone https://github.com/Volcann/M2MasterBot.git
cd M2MasterBot

# Set up virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🎮 Running the Bots

All scripts are run from the project root with `PYTHONPATH=src`.

```bash
# Play manually
PYTHONPATH=src python3 src/run_manual.py

# Heuristic bots
PYTHONPATH=src python3 src/run_heuristic_bot.py     # BasicBot (recommended)
PYTHONPATH=src python3 src/run_fixed_linear_bot.py   # FixedLinearBot (static weights)
PYTHONPATH=src python3 src/run_adaptive_linear_bot.py # AdaptiveLinearBot (uniform start)
PYTHONPATH=src python3 src/run_linear_bot.py        # LinearBot (pre-tuned + adaptive)

# RL bots
PYTHONPATH=src python3 src/run_rl.py                # Teacher-trained RL agent
PYTHONPATH=src python3 src/run_rl_no_teacher.py     # Self-taught RL agent
```

### RL Training

```bash
# Train with teacher guidance (stable, faster convergence)
PYTHONPATH=src python3 -m training.rl.train_with_teacher

# Train without teacher (observe the failure-and-recovery cycle)
PYTHONPATH=src python3 -m training.rl.train_standard --episodes 200 --lr 0.1
```

---

## 📂 Project Structure

```
src/
├── agents/
│   ├── heuristic/
│   │   ├── basic_bot.py          # Normalized heuristic (recommended)
│   │   ├── linear.py             # Pre-tuned adaptive weights
│   │   ├── fixed_linear.py       # Static, non-learning weights
│   │   └── adaptive_linear.py    # Uniform start, learns from scratch
│   └── rl/
│       ├── teacher.py            # RL agent trained with heuristic teacher
│       └── standard.py           # RL agent trained without teacher
├── core/                         # Game logic and engine
├── ui/                           # Pygame UI and visualizers
└── training/rl/                  # RL training scripts
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🎉 Credits

Created by **volcani** — inspired by the mechanics of **2048**, with a focus on making AI research approachable and visual.

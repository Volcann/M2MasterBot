# M2 Merge Block Bot

![M2 Merge Block Game](https://github.com/Volcann/M2MasterBot/blob/92beb45387ec467a4a7d8915338a2f26dbbdc424/assets/image.png)

A comprehensive Reinforcement Learning (RL) and Heuristic-based AI framework for the **M2 Merge Block** game. This project serves as both a high-performance game bot and a research platform for observing RL dynamics, including real-time weight visualization and catastrophic failure cycles.

---

## 🚀 Key Features

### 🧠 Multi-Strategy AI
- **Heuristic Engine**: A deterministic bot using hand-tuned weighted features to achieve consistent high scores.
- **Guided RL (Teacher-Student)**: An agent trained using heuristic guidance to accelerate convergence and stability.
- **Research RL (No-Teacher)**: A "pure" RL implementation using sparse rewards and epsilon-greedy exploration, designed to demonstrate the "Catastrophic Failure" cycle in deep reinforcement learning.

### 📊 Real-Time Visualization
- **Neural Weight Sparklines**: Live tracking of model weight volatility.
- **Performance Metrics**: Real-time display of scores, rewards, and exploration (epsilon) rates.
- **Collapse Warnings**: Visual indicators for weight divergence and training instability.

---

## 🛠 AI Strategies

### 1. Heuristic Bot
The heuristic engine evaluates potential moves based on six key board features:

| Feature | Description |
|:---|:---|
| **Score** | Immediate points gained from the move. |
| **Empty Cells** | Maximizing available space on the 5x7 grid. |
| **Merge Count** | Number of successful merges triggered. |
| **Monotonicity** | Maintaining a logical gradient of values across rows/columns. |
| **Smoothness** | Minimizing value variance between adjacent blocks. |
| **Corner Bonus** | Keeping high-value tiles anchored in the corners. |

### 2. Reinforcement Learning
Supported RL paradigms include:
- **Q-Learning Implementation**: Linear function approximation using the same feature set as the heuristic bot.
- **Exploration Policy**: Epsilon-greedy decay starting from 100% exploration.
- **Sparse Rewards**: In Research Mode, the agent is only rewarded for high-value merges (e.g., ≥ 128), making the environment highly challenging.

---

## 🏃 Getting Started

### Prerequisites
- **Python 3.10+**
- **Pygame** (for UI and Visualization)
- **NumPy**

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Volcann/M2MasterBot.git
   cd M2MasterBot
   ```
2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 Execution Commands

### Play the Game
Test your skills against the AI or play manually:
```bash
python run_bot.py      # Run the Heuristic Bot
python main.py         # Play Manually (Controls: Mouse or 0-4)
```

### RL Training & Research
Observe the agent's learning process in real-time:

#### Guided Training (Stable)
```bash
PYTHONPATH=src python3 -m training.train_agent
```

#### No-Teacher Training (Visualize Failure Cycle)
```bash
PYTHONPATH=src python3 -m training.train_no_teacher --episodes 200 --lr 0.1
```

---

## 📂 Project Structure
- `src/core`: Game logic and engine.
- `src/heuristic_bot`: Heuristic decision logic.
- `src/rl_agent_with_teacher`: Guided RL implementation.
- `src/rl_no_teacher`: Sparse reward RL for research.
- `src/ui`: Pygame-based GUI and real-time visualizers.
- `src/training`: Training scripts and performance evaluation.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Credits
Created by **volcani** | Inspired by the addictive mechanics of **2048**.
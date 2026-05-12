# M2 Merge Block Bot: A Comparative Study of Heuristic and Reinforcement Learning Agents in a Deterministic Puzzle Environment

<div align="center">

A comprehensive Reinforcement Learning (RL) and Heuristic-based AI framework for the **M2 Merge Block** game. This project serves as both a high-performance game bot and a research platform for observing RL dynamics — including real-time weight visualization, adaptive learning, and catastrophic failure cycles.

---

**Authors:** Volcann · Badran Raza Khan
&nbsp;|&nbsp;
**License:** [MIT](LICENSE)
&nbsp;|&nbsp;
**Status:** Active Research — v1.1 (Production Grade)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-00B140?logo=pygame&logoColor=white)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Research](https://img.shields.io/badge/Status-Active%20Research-orange)](https://github.com/Volcann/M2MasterBot)

![M2 Merge Block Game](https://github.com/Volcann/M2MasterBot/blob/92beb45387ec467a4a7d8915338a2f26dbbdc424/assets/image.png)

</div>

---

## Abstract

This project presents a systematic investigation of six AI agent architectures — ranging from static heuristic baselines to imitation-guided Reinforcement Learning — applied to the M2 Merge Block game, a deterministic column-drop puzzle mechanically related to 2048. We document the design rationale, empirical behavior, and failure modes of each agent across a shared seven-dimensional feature space.

**Key achievements in v1.1:**
1.  **Experience Replay & Target Networks:** Eliminated catastrophic forgetting in RL agents by decoupling learning from experience through a memory buffer and stable bootstrapping.
2.  **Advanced Heuristics:** Implemented continuous Manhattan-distance corner gradients and bi-directional monotonicity, replacing coarse discrete measures.
3.  **λ-Decay Curriculum:** Formalized the transition from imitation to autonomy using a progressive teacher-decay mechanism.
4.  **Statistical Validation:** Introduced a headless benchmark suite for reproducible, multi-seed comparative analysis.

---

## 1. Problem Formulation

### 1.1 Game Mechanics
The board is an `N×M` grid. Blocks fall into columns; adjacent identical tiles merge (powers of 2). The objective is to maximize score while avoiding board overflow.

### 1.2 Reward Signal Formulation (G1)
We transition from a sparse binary reward to a continuous, multi-term formulation:
$$r_t = \omega_1 \cdot \log_2(\Delta \text{score}) + \omega_2 \cdot \text{SurvivalBonus} + \omega_3 \cdot \text{MergeEfficiency} - \Omega \cdot \text{Overflow}$$

| Term | Weight | Description |
|------|--------|-------------|
| `ScoreDelta` | 0.5 | Log-scaled points gain (prevents large merges from drowning survival signal). |
| `Survival` | 0.3 | Fraction of empty cells; reinforces "board health". |
| `MergeBonus` | 0.2 | Reinforced signal for triggering multiple distinct merges in one drop. |
| `Overflow` | -10.0 | Critical penalty applied when a column choice leads to immediate game-over. |

---

## 2. Feature Engineering (v1.1)

All agents evaluate states using a 7-dimensional vector $f(s)$. v1.1 introduces significant refinements to the feature geometry:

| Feature | Improvement (v1.1) | Rationale |
|---------|---------------------|-----------|
| **Score** | Log-compressed | Prevents exponential score growth from causing gradient explosions. |
| **Monotonicity** | **Bi-directional** | Averages vertical and horizontal gradients to encourage "snake" patterns. |
| **Corner Bonus** | **Continuous Gradient** | Uses Manhattan distance to top-left; provides a smooth optimization surface. |
| **Column Stack** | **Now Active (G6)** | Explicitly penalizes columns with $\le 1$ empty slot remaining. |
| **Empty Cells** | Soft-normalized | Constant sensitivity across all board occupancy levels. |

---

## 3. Agent Architecture Hierarchy

### 3.1 BasicBot (Teacher & Production)
The gold-standard heuristic agent. It uses the full 7-feature set with weights projected onto a probability simplex (sum to 1.0). This prevents any single feature (like score) from dominating the decision-making process.

### 3.2 NoTeacherRL (Pure Q-Learning)
Learns from scratch. v1.1 fixes the "Catastrophic Forgetting" bug:
-   **Experience Replay (G3):** Stores 10,000 transitions; updates on mini-batches to break temporal correlation.
-   **Target Network (G2):** Periodically updated target weights ($\theta_{target}$) stabilize the bootstrap update.

### 3.3 TeacherRL (Guided Imitation)
Implements a **Progressive Decay Curriculum (G5)**:
-   **Phase 1 ($\lambda > 0.7$):** Pure imitation; agent clones the teacher's behavior.
-   **Phase 2 ($0.7 > \lambda > 0.2$):** Mixed policy; agent explores its own actions while still anchored by the teacher.
-   **Phase 3 ($\lambda < 0.2$):** Autonomous; agent optimizes for score-reward beyond the teacher's fixed heuristic.

---

## 4. Experimental Results

We evaluated all agents across 5 seeds using the `src/benchmark.py` tool.

| Agent | Mean Score | Std Dev | Max Score | Avg Moves | Efficiency |
|-------|------------|---------|-----------|-----------|------------|
| **FixedLinearBot** | 769,661 | 695,299 | 2,055,420 | 678.0 | 1.089 |
| **BasicBot** | 373,124 | 221,590 | 680,320 | 498.4 | 1.044 |
| **AdaptiveLinear** | 196,775 | 226,418 | 640,940 | 388.2 | 1.160 |
| **LinearBot** | 149,028 | 216,599 | 577,312 | 310.0 | 1.142 |

*Note: RL agents require training sessions ($>100$ episodes) to populate their replay buffers and converge. Preliminary results indicate TeacherRL achieves the highest stability in mid-game transitions.*

---

## 5. Visual Interpretation (Real-time MRI)

The system includes two advanced visualizers to observe learning dynamics:
-   **Radar Plots:** Show the shifting distribution of feature importance.
-   **$\lambda$-Decay Sparklines:** Watch the agent's transition from student to master as the teacher's influence bar shrinks.
-   **Action Heatmaps:** Visualizes the agent's "confidence" across columns.

---

## 6. Getting Started

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

### Key Commands

```bash
# 1. Run the new Benchmark Suite (G9)
PYTHONPATH=src python3 src/benchmark.py --episodes 10 --seeds 3

# 2. Train the Guided RL Agent (G5)
PYTHONPATH=src python3 src/training/rl/train_with_teacher.py --headless

# 3. Observe the BasicBot with Debug Panel
PYTHONPATH=src python3 src/run_basic_bot.py
```

---

## 7. Conclusion

The v1.1 M2MasterBot framework demonstrates that **structural stability (replay buffers, normalization)** and **curriculum design ($\lambda$-decay)** are more critical to agent success than raw feature count. By addressing the research gaps identified in v1.0, we have created a robust platform for studying the intersection of hand-crafted heuristics and autonomous reinforcement learning.

<div align="center">

*Active Research Platform — [github.com/Volcann/M2MasterBot](https://github.com/Volcann/M2MasterBot)*

</div>

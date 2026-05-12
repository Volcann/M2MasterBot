import json
import os
import copy
import random
import numpy as np
from collections import deque
from typing import List, Optional
from config.constants import GRID_WIDTH
from agents.heuristic.basic_bot import BasicBot


class NoTeacherAgent:
    def __init__(
        self,
        initial_weights: Optional[List[float]] = None,
        learning_rate: float = 0.1,
        gamma: float = 0.95,
        replay_buffer_size: int = 10_000,
        batch_size: int = 64,
    ):
        self.feature_names = ["score", "empty", "merge", "mono", "smooth", "corner", "stack"]
        if initial_weights is None:
            initial_weights = np.random.uniform(-0.1, 0.1, len(self.feature_names)).tolist()
        self.theta = np.array(initial_weights, dtype=float)
        self.learning_rate = float(learning_rate)
        self.gamma = float(gamma)
        self.rl_bot = BasicBot()
        self.replay_buffer: deque = deque(maxlen=replay_buffer_size)
        self.batch_size = batch_size
        self.target_theta = self.theta.copy()
        self.update_count = 0
        self.target_update_freq = 500

    def _feature_vector_from_dict(self, features: dict) -> np.ndarray:
        return np.array([features[key] for key in self.feature_names], dtype=float)

    def _get_action_space_features(
        self, matrix: List[List[int]], next_value: int
    ) -> List[Optional[np.ndarray]]:
        feature_vectors = []
        for col in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, merges = self.rl_bot.simulate_move(temp_matrix, col, next_value)
            if score_gain == -1:
                feature_vectors.append(None)
                continue
            features = self.rl_bot.compute_features(col, temp_matrix, score_gain, merges)
            feature_vectors.append(self._feature_vector_from_dict(features))
        return feature_vectors

    def select_action(
        self,
        matrix: List[List[int]],
        next_value: int,
        epsilon: float = 0.1,
        deterministic: bool = False,
    ) -> int:
        if deterministic:
            epsilon = 0.0
        feature_vectors = self._get_action_space_features(matrix, next_value)
        logits = np.array(
            [np.dot(self.theta, v) if v is not None else -1e9 for v in feature_vectors]
        )
        if np.random.random() < epsilon:
            valid_actions = [i for i, v in enumerate(feature_vectors) if v is not None]
            return np.random.choice(valid_actions) if valid_actions else 0
        return int(np.argmax(logits))

    def update_q_learning(
        self,
        state_features: np.ndarray,
        reward: float,
        next_state_matrix: Optional[List[List[int]]],
        next_value: Optional[int],
        done: bool,
    ) -> float:
        self.replay_buffer.append((
            state_features.copy(),
            reward,
            [row[:] for row in next_state_matrix] if next_state_matrix is not None else None,
            next_value,
            done,
        ))

        if len(self.replay_buffer) < self.batch_size:
            return 0.0

        batch = random.sample(self.replay_buffer, self.batch_size)
        total_delta = 0.0

        for sf, r, nsm, nv, d in batch:
            current_q = np.dot(self.theta, sf)
            if d or nsm is None or nv is None:
                target = r
            else:
                next_features = self._get_action_space_features(nsm, nv)
                next_qs = [
                    np.dot(self.target_theta, v) if v is not None else -1e9
                    for v in next_features
                ]
                target = r + self.gamma * np.max(next_qs)
            
            error = target - current_q
            delta_w = self.learning_rate * error * sf
            self.theta += delta_w
            total_delta += np.mean(np.abs(delta_w))

        self.update_count += 1
        if self.update_count % self.target_update_freq == 0:
            self.target_theta = self.theta.copy()

        return total_delta / self.batch_size

    def get_weights(self) -> np.ndarray:
        return self.theta

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "theta": self.theta.tolist(),
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def load(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        loaded_theta = np.array(data.get("theta", self.theta), dtype=float)
        if len(loaded_theta) == len(self.theta):
            self.theta = loaded_theta
        elif len(loaded_theta) < len(self.theta):
            pad = np.random.uniform(-0.05, 0.05, len(self.theta) - len(loaded_theta))
            self.theta = np.concatenate([loaded_theta, pad])
        else:
            self.theta = loaded_theta[: len(self.theta)]
        self.learning_rate = float(data.get("learning_rate", self.learning_rate))
        self.gamma = float(data.get("gamma", self.gamma))

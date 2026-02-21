import json
import os
import copy
import numpy as np
from typing import List, Optional

from config.constants import GRID_WIDTH
from heuristic_bot.bot import HeuristicBot


class NoTeacherAgent:
    def __init__(
        self,
        initial_weights: Optional[List[float]] = None,
        learning_rate: float = 0.1,
        gamma: float = 0.95
    ):
        self.feature_names = [
            "score", "empty", "merge", "mono", "smooth", "corner"
        ]
        # High volatility initialization for visual effect
        if initial_weights is None:
            initial_weights = np.random.uniform(-0.1, 0.1, len(self.feature_names)).tolist()

        self.theta = np.array(initial_weights, dtype=float)
        self.learning_rate = float(learning_rate)
        self.gamma = float(gamma)
        self.rl_bot = HeuristicBot()
        
    def _feature_vector_from_dict(self, features: dict) -> np.ndarray:
        return np.array(
            [features[key] for key in self.feature_names],
            dtype=float
        )

    def _get_action_space_features(
        self,
        matrix: List[List[int]],
        next_value: int
    ) -> List[Optional[np.ndarray]]:
        feature_vectors = []
        for col in range(GRID_WIDTH):
            temp_matrix = copy.deepcopy(matrix)
            score_gain, merges = self.rl_bot.simulate_move(
                temp_matrix, col, next_value
            )

            if score_gain == -1:
                feature_vectors.append(None)
                continue

            features = self.rl_bot.compute_features(
                col, temp_matrix, score_gain, merges
            )
            feature_vectors.append(self._feature_vector_from_dict(features))
        return feature_vectors

    def select_action(
        self,
        matrix: List[List[int]],
        next_value: int,
        epsilon: float = 0.1
    ) -> int:
        feature_vectors = self._get_action_space_features(matrix, next_value)
        logits = np.array([
            np.dot(self.theta, v) if v is not None else -1e9
            for v in feature_vectors
        ])

        # Epsilon-greedy exploration
        if np.random.random() < epsilon:
            valid_actions = [i for i, v in enumerate(feature_vectors) if v is not None]
            if not valid_actions: return 0
            return np.random.choice(valid_actions)
        
        return int(np.argmax(logits))

    def update_q_learning(
        self,
        state_features: np.ndarray,
        reward: float,
        next_state_matrix: Optional[List[List[int]]],
        next_value: Optional[int],
        done: bool
    ) -> float:
        """
        Q(s, a) = weights * features
        Target = R + gamma * max(Q(s', a'))
        Error = Target - Q(s, a)
        Grad = Error * Features
        """
        current_q = np.dot(self.theta, state_features)
        
        if done or next_state_matrix is None or next_value is None:
            target = reward
        else:
            next_features = self._get_action_space_features(next_state_matrix, next_value)
            next_qs = [
                np.dot(self.theta, v) if v is not None else -1e9
                for v in next_features
            ]
            target = reward + self.gamma * np.max(next_qs)

        error = target - current_q
        delta_w = self.learning_rate * error * state_features
        self.theta += delta_w
        
        return np.mean(np.abs(delta_w))

    def get_weights(self) -> np.ndarray:
        return self.theta

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "theta": self.theta.tolist(),
            "learning_rate": self.learning_rate,
            "gamma": self.gamma
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def load(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.theta = np.array(data.get("theta", self.theta), dtype=float)
        self.learning_rate = float(
            data.get("learning_rate", self.learning_rate)
        )
        self.gamma = float(data.get("gamma", self.gamma))

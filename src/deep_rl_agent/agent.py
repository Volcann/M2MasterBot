import json
import os
import copy
import numpy as np
from typing import List, Optional

from config.constants import GRID_WIDTH
from heuristic_bot.bot import HeuristicBot


class RLAgent:
    def __init__(
        self,
        initial_weights: Optional[List[float]] = None,
        learning_rate: float = 0.01,
        gamma: float = 0.99
    ):
        self.feature_names = [
            "score", "empty", "merge", "mono", "smooth", "corner"
        ]
        if initial_weights is None:
            initial_weights = [0.15, 0.3, 0.1, 0.15, 0.15, 0.15]

        self.theta = np.array(initial_weights, dtype=float)
        self.learning_rate = float(learning_rate)
        self.gamma = float(gamma)
        self.rl_bot = HeuristicBot()
        self.episode_log = []

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

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        shifted_logits = logits - np.max(logits)
        exp_values = np.exp(shifted_logits)
        return exp_values / np.sum(exp_values)

    def train_from_heuristic(
        self,
        matrix: List[List[int]],
        next_value: int
    ) -> int:
        teacher_action = self.rl_bot.solve(matrix, next_value)
        feature_vectors = self._get_action_space_features(matrix, next_value)

        logits = np.array([
            np.dot(self.theta, v) if v is not None else -1e9
            for v in feature_vectors
        ])
        probabilities = self._softmax(logits)

        target = np.zeros(GRID_WIDTH)
        target[teacher_action] = 1.0

        gradient = np.zeros_like(self.theta)
        for i, vec in enumerate(feature_vectors):
            if vec is not None:
                gradient += (target[i] - probabilities[i]) * vec

        self.theta += self.learning_rate * gradient
        return teacher_action

    def select_action(
        self,
        matrix: List[List[int]],
        next_value: int,
        deterministic: bool = True
    ) -> int:
        feature_vectors = self._get_action_space_features(matrix, next_value)
        logits = np.array([
            np.dot(self.theta, v) if v is not None else -1e9
            for v in feature_vectors
        ])

        if deterministic:
            return int(np.argmax(logits))

        probabilities = self._softmax(logits)
        return int(np.random.choice(len(probabilities), p=probabilities))

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

import json
import os
import copy
import numpy as np
from typing import List, Optional
from config.constants import GRID_WIDTH
from agents.heuristic.basic_bot import BasicBot


class RLAgent:
    def __init__(
        self,
        initial_weights: Optional[List[float]] = None,
        learning_rate: float = 0.01,
        gamma: float = 0.99,
        teacher_lambda: float = 1.0,
        lambda_decay: float = 0.995,
        lambda_min: float = 0.05,
    ):
        self.feature_names = ["score", "empty", "merge", "mono", "smooth", "corner", "stack"]
        if initial_weights is None:
            initial_weights = [0.10, 0.25, 0.10, 0.15, 0.15, 0.15, 0.10]
        self.theta = np.array(initial_weights, dtype=float)
        self.learning_rate = float(learning_rate)
        self.gamma = float(gamma)
        self.teacher_lambda = float(teacher_lambda)
        self.lambda_decay = float(lambda_decay)
        self.lambda_min = float(lambda_min)
        self.rl_bot = BasicBot()
        self.episode_log = []
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

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        shifted = logits - np.max(logits)
        exp_v = np.exp(shifted)
        return exp_v / np.sum(exp_v)

    def select_action_with_teacher(
        self, matrix: List[List[int]], next_value: int
    ) -> tuple:
        teacher_action = self.rl_bot.solve(matrix, next_value)
        feature_vectors = self._get_action_space_features(matrix, next_value)
        logits = np.array(
            [np.dot(self.theta, v) if v is not None else -1e9 for v in feature_vectors]
        )
        agent_action = int(np.argmax(logits))
        if np.random.random() < self.teacher_lambda:
            chosen_action = teacher_action
        else:
            chosen_action = agent_action
        self.teacher_lambda = max(self.lambda_min, self.teacher_lambda * self.lambda_decay)
        state_features = (
            feature_vectors[chosen_action]
            if feature_vectors[chosen_action] is not None
            else np.zeros(len(self.feature_names))
        )
        return chosen_action, state_features, teacher_action, agent_action

    def update_q_learning(
        self,
        state_features: np.ndarray,
        reward: float,
        next_state_matrix: Optional[List[List[int]]],
        next_value: Optional[int],
        done: bool,
    ) -> float:
        current_q = np.dot(self.theta, state_features)
        if done or next_state_matrix is None or next_value is None:
            target = reward
        else:
            next_features = self._get_action_space_features(next_state_matrix, next_value)
            next_qs = [
                np.dot(self.target_theta, v) if v is not None else -1e9
                for v in next_features
            ]
            target = reward + self.gamma * np.max(next_qs)
        error = target - current_q
        delta_w = self.learning_rate * error * state_features
        self.theta += delta_w
        self.update_count += 1
        if self.update_count % self.target_update_freq == 0:
            self.target_theta = self.theta.copy()
        return float(np.mean(np.abs(delta_w)))

    def train_from_heuristic(self, matrix: List[List[int]], next_value: int) -> int:
        teacher_action = self.rl_bot.solve(matrix, next_value)
        feature_vectors = self._get_action_space_features(matrix, next_value)
        logits = np.array(
            [np.dot(self.theta, v) if v is not None else -1e9 for v in feature_vectors]
        )
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
        self, matrix: List[List[int]], next_value: int, deterministic: bool = True
    ) -> int:
        feature_vectors = self._get_action_space_features(matrix, next_value)
        logits = np.array(
            [np.dot(self.theta, v) if v is not None else -1e9 for v in feature_vectors]
        )
        if deterministic:
            return int(np.argmax(logits))
        return int(np.random.choice(len(logits), p=self._softmax(logits)))

    def get_weights(self) -> np.ndarray:
        return self.theta

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "theta": self.theta.tolist(),
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "teacher_lambda": self.teacher_lambda,
            "lambda_decay": self.lambda_decay,
            "lambda_min": self.lambda_min,
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
        self.teacher_lambda = float(data.get("teacher_lambda", self.teacher_lambda))
        self.lambda_decay = float(data.get("lambda_decay", self.lambda_decay))
        self.lambda_min = float(data.get("lambda_min", self.lambda_min))

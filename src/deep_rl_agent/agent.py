import json
import os
import numpy as np
from typing import List
from deep_rl_agent.feature_extractor import FeatureExtractor


class RLAgent:
    def __init__(self, initial_weights=None, learning_rate=0.01, gamma=0.99):
        self.feature_names = ["score", "empty", "merge", "mono", "smooth", "corner"]
        if initial_weights is None:
            initial_weights = [0.15, 0.3, 0.1, 0.15, 0.15, 0.15]
        self.theta = np.array(initial_weights, dtype=float)
        self.learning_rate = float(learning_rate)
        self.gamma = float(gamma)
        self.extractor = FeatureExtractor()
        self.episode_log = []
        self.baseline = 0.0
        self.baseline_alpha = 0.01

    def _feature_vector_from_dict(self, features: dict) -> np.ndarray:
        return np.array([features[k] for k in self.feature_names], dtype=float)

    def _compute_action_features(self, matrix, next_value) -> List[np.ndarray]:
        feature_vecs = []
        for col in range(self.extractor.grid_width):
            score_gain, merges, temp_matrix = self.extractor.simulate_move(matrix, col, next_value)
            if score_gain == -1:
                feature_vecs.append(None)
                continue
            features = self.extractor.compute_features(col, temp_matrix, score_gain, merges)
            feature_vecs.append(self._feature_vector_from_dict(features))
        return feature_vecs

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        shifted = logits - np.max(logits)
        exps = np.exp(shifted)
        denom = np.sum(exps)
        if denom == 0:
            return np.ones_like(exps) / len(exps)
        return exps / denom

    def select_action(self, matrix, next_value, deterministic=False):
        feature_vecs = self._compute_action_features(matrix, next_value)
        logits = []
        for vec in feature_vecs:
            if vec is None:
                logits.append(-1e9)
            else:
                logits.append(float(np.dot(self.theta, vec)))
        logits = np.array(logits, dtype=float)
        probs = self._softmax(logits)
        valid = [i for i, v in enumerate(feature_vecs) if v is not None]
        if len(valid) == 0:
            return 0
        if deterministic:
            return int(np.argmax(probs))
        action = int(np.random.choice(len(probs), p=probs))
        self.episode_log.append((feature_vecs, action, probs))
        return action

    def finish_episode(self, rewards: List[float]):
        returns = []
        G = 0.0
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        returns = np.array(returns, dtype=float)
        if len(returns) == 0:
            return
        self.baseline = (1 - self.baseline_alpha) * self.baseline + self.baseline_alpha * float(np.mean(returns))
        for t, (feature_vecs, action, probs) in enumerate(self.episode_log):
            vec = feature_vecs[action]
            if vec is None:
                continue
            advantage = returns[t] - self.baseline
            expected = sum(p * (fv if fv is not None else 0) for p, fv in zip(probs, feature_vecs))
            grad_log = vec - expected
            self.theta += self.learning_rate * advantage * grad_log
        self.episode_log = []

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {"theta": self.theta.tolist(), "learning_rate": self.learning_rate, "gamma": self.gamma}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def load(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.theta = np.array(data.get("theta", self.theta), dtype=float)
        self.learning_rate = float(data.get("learning_rate", self.learning_rate))
        self.gamma = float(data.get("gamma", self.gamma))

import os
from deep_rl_agent.agent import RLAgent


class GameBot:
    def __init__(self, model_path: str = "data/rl_agent.json"):
        self.model_path = model_path
        self.rl_agent = RLAgent()
        self.rl_agent.load(self.model_path)

    def solve(self, matrix, next_value):
        return self.rl_agent.select_action(matrix, next_value, deterministic=True)

    def act(self, matrix, next_value):
        return self.rl_agent.select_action(matrix, next_value, deterministic=False)

    def save_policy(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.rl_agent.save(self.model_path)

    def load_policy(self):
        self.rl_agent.load(self.model_path)

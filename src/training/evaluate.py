import numpy as np
from core.game_logic import GameLogic
from deep_rl_agent.agent import RLAgent


def evaluate(episodes=100):
    agent = RLAgent()
    agent.load("data/rl_agent.json")

    scores = []
    for _ in range(episodes):
        game = GameLogic()
        next_value = game.get_random_value()
        while True:
            matrix = game.get_matrix()
            if game_over(matrix, next_value):
                break
            action = agent.select_action(matrix, next_value, deterministic=True)
            merged, count = game.add_to_column(next_value, action)
            if not merged:
                break
            next_value = game.get_random_value()
        scores.append(game.get_score())
    return scores


if __name__ == "__main__":
    from core.utils.utils import game_over
    scores = evaluate(episodes=200)
    print("Avg score:", np.mean(scores))
    print("Max score:", np.max(scores))

import argparse
import numpy as np
from core.game_logic import GameLogic
from core.utils.utils import game_over, rearrange
from rl_agent_with_teacher.agent import RLAgent


def evaluate(episodes=100, model_path="data/rl_agent.json"):
    agent = RLAgent()
    agent.load(model_path)

    scores = []
    for ep in range(episodes):
        game = GameLogic()
        next_value = game.get_random_value()

        while True:
            matrix = game.get_matrix()
            if game_over(matrix, next_value):
                break
            action = agent.select_action(matrix, next_value, deterministic=True)
            merged, _ = game.add_to_column(next_value, action)
            if not merged:
                break

            new_matrix = rearrange(game.get_matrix())
            game.set_matrix(new_matrix)
            game.merge_column()

            next_value = game.get_random_value()
        final_score = game.get_score()
        scores.append(final_score)
        print(f"Eval Episode {ep+1}: {final_score}")

    return scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M2MasterBot RL Evaluation")
    parser.add_argument("--episodes", type=int, default=100, help="Number of episodes to evaluate")
    parser.add_argument("--model-path", type=str, default="data/rl_agent.json", help="Path to model file")

    args = parser.parse_args()

    results = evaluate(episodes=args.episodes, model_path=args.model_path)
    print("\n--- Evaluation Results ---")
    print(f"Average Score: {np.mean(results):.2f}")
    print(f"Maximum Score: {np.max(results)}")

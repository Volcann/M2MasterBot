import argparse
import numpy as np
from core.game_logic import GameLogic
from core.utils.utils import game_over, rearrange
from rl_no_teacher.agent import NoTeacherAgent


def evaluate_no_teacher(episodes=100, model_path="data/rl_no_teacher_agent.json"):
    agent = NoTeacherAgent()
    agent.load(model_path)

    scores = []
    for ep in range(episodes):
        game = GameLogic()
        next_value = game.get_random_value()

        while True:
            matrix = game.get_matrix()
            if game_over(matrix, next_value):
                break
            
            # Use greedy action selection for evaluation
            action = agent.select_action(matrix, next_value, epsilon=0.0)
            merged, _ = game.add_to_column(next_value, action)
            if not merged:
                break

            new_matrix = rearrange(game.get_matrix())
            game.set_matrix(new_matrix)
            game.merge_column()

            next_value = game.get_random_value()
            
        final_score = game.get_score()
        scores.append(final_score)
        print(f"No-Teacher Eval Episode {ep+1}: {final_score}")

    return scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M2MasterBot No-Teacher RL Evaluation")
    parser.add_argument("--episodes", type=int, default=50, help="Number of episodes")
    parser.add_argument("--model-path", type=str, default="data/rl_no_teacher_agent.json", help="Path to model")

    args = parser.parse_args()

    results = evaluate_no_teacher(episodes=args.episodes, model_path=args.model_path)
    print("\n--- No-Teacher Evaluation Results ---")
    print(f"Average Score: {np.mean(results):.2f}")
    print(f"Maximum Score: {np.max(results)}")

import argparse
import numpy as np
from typing import Callable, List, Dict
from core.game_logic import GameLogic
from core.utils.core_utils import game_over, rearrange


def run_episode_headless(solve_fn: Callable, seed: int = 0) -> Dict:
    np.random.seed(seed)
    game = GameLogic()
    next_value = game.get_random_value()
    total_merges = 0
    total_moves = 0
    while True:
        matrix = game.get_matrix()
        if game_over(matrix, next_value):
            break
        action = solve_fn(matrix, next_value)
        merged, count = game.add_to_column(next_value, action)
        if not merged:
            break
        total_merges += count
        total_moves += 1
        new_matrix = rearrange(game.get_matrix())
        game.set_matrix(new_matrix)
        game.merge_column()
        next_value = game.get_random_value()
    final_score = game.get_score() if hasattr(game, "get_score") else total_merges
    return {
        "score": float(final_score),
        "moves": total_moves,
        "merge_efficiency": total_merges / max(total_moves, 1),
    }


def make_fixed_linear():
    from agents.heuristic.fixed_linear import FixedLinearBot
    bot = FixedLinearBot()
    return lambda m, v: bot.solve(m, v)


def make_adaptive_linear():
    from agents.heuristic.adaptive_linear import AdaptiveLinearBot
    bot = AdaptiveLinearBot()
    return lambda m, v: bot.solve(m, v)


def make_linear():
    from agents.heuristic.linear import LinearBot
    bot = LinearBot()
    return lambda m, v: bot.solve(m, v)


def make_basic_bot():
    from agents.heuristic.basic_bot import BasicBot
    bot = BasicBot()
    return lambda m, v: bot.solve(m, v)


def make_no_teacher(model_path: str = "data/rl_no_teacher_agent.json"):
    from agents.rl.standard import NoTeacherAgent
    agent = NoTeacherAgent()
    agent.load(model_path)
    return lambda m, v: agent.select_action(m, v, epsilon=0.0)


def make_teacher_rl(model_path: str = "data/rl_agent.json"):
    from agents.rl.teacher import RLAgent
    agent = RLAgent()
    agent.load(model_path)
    return lambda m, v: agent.select_action(m, v, deterministic=True)


AGENTS = [
    ("FixedLinearBot",   make_fixed_linear),
    ("AdaptiveLinear",   make_adaptive_linear),
    ("LinearBot",        make_linear),
    ("BasicBot",         make_basic_bot),
    ("NoTeacherRL",      make_no_teacher),
    ("TeacherRL",        make_teacher_rl),
]


def evaluate_agent(name: str, factory_fn: Callable, n_episodes: int, n_seeds: int) -> Dict:
    all_scores, all_moves, all_efficiency = [], [], []
    for seed in range(n_seeds):
        solve_fn = factory_fn()
        for ep in range(n_episodes):
            result = run_episode_headless(solve_fn, seed=seed * 10000 + ep)
            all_scores.append(result["score"])
            all_moves.append(result["moves"])
            all_efficiency.append(result["merge_efficiency"])
    return {
        "name":             name,
        "mean_score":       float(np.mean(all_scores)),
        "std_score":        float(np.std(all_scores)),
        "max_score":        float(np.max(all_scores)),
        "mean_moves":       float(np.mean(all_moves)),
        "merge_efficiency": float(np.mean(all_efficiency)),
        "n_runs":           len(all_scores),
    }


def print_table(results: List[Dict]):
    results_sorted = sorted(results, key=lambda r: r["mean_score"])
    header = (
        f"{'Rank':<5} {'Agent':<18} {'Mean Score':>12} {'± Std':>9} "
        f"{'Max Score':>10} {'Avg Moves':>10} {'Merge/Move':>11}"
    )
    print("\n" + "─" * len(header))
    print(header)
    print("─" * len(header))
    for rank, r in enumerate(results_sorted, 1):
        print(
            f"{rank:<5} {r['name']:<18} "
            f"{r['mean_score']:>12.1f} "
            f"{r['std_score']:>9.1f} "
            f"{r['max_score']:>10.1f} "
            f"{r['mean_moves']:>10.1f} "
            f"{r['merge_efficiency']:>11.3f}"
        )
    print("─" * len(header))
    print(f"  (Each agent evaluated over {results_sorted[0]['n_runs']} total runs)\n")


def main():
    parser = argparse.ArgumentParser(
        description="M2MasterBot — multi-agent benchmark"
    )
    parser.add_argument("--episodes", type=int, default=20,
                        help="Episodes per seed per agent")
    parser.add_argument("--seeds", type=int, default=3,
                        help="Number of random seeds")
    parser.add_argument("--no-teacher-path", type=str,
                        default="data/rl_no_teacher_agent.json")
    parser.add_argument("--teacher-path", type=str, default="data/rl_agent.json")
    parser.add_argument("--skip-rl", action="store_true",
                        help="Skip RL agents")
    args = parser.parse_args()
    agents_to_run = AGENTS if not args.skip_rl else AGENTS[:4]
    results = []
    for name, factory in agents_to_run:
        print(f"  Evaluating {name} ...", flush=True)
        try:
            r = evaluate_agent(name, factory, args.episodes, args.seeds)
            results.append(r)
        except Exception as e:
            print(f"    ⚠  Skipped {name}: {e}")
    if results:
        print_table(results)


if __name__ == "__main__":
    main()

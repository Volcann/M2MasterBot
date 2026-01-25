
import os

from deep_rl_agent.bot_runner import BotRunner


if __name__ == "__main__":
    os.environ["PYTHONPATH"] = "src"
    runner = BotRunner(model_path="data/rl_agent.json", move_interval_ms=100, fps=30)
    runner.run()

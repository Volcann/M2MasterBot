
import os

from ui.rl_bot.rl_bot_ui import RLBotUI


if __name__ == "__main__":
    os.environ["PYTHONPATH"] = "src"
    runner = RLBotUI(model_path="data/rl_agent.json", move_interval_ms=100, fps=30)
    runner.run()

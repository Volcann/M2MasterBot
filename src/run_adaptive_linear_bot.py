from core.game_logic import GameLogic
from ui.agents.heuristic.adaptive_linear_bot_ui import AdaptiveLinearBotUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = AdaptiveLinearBotUI(game_logic)
    game_ui.run()

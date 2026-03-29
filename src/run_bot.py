from core.game_logic import GameLogic
from ui.agents.heuristic.heuristic_bot_ui import HeuristicBotUI
from ui.agents.heuristic.linear_bot_ui import LinearBotUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = HeuristicBotUI(game_logic)
    game_ui.run()

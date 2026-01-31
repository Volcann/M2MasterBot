from core.game_logic import GameLogic
from ui.heuristic_bot.heuristic_bot_ui import HeuristicBotUI
from ui.heuristic_bot.linear_bot_ui import LinearBotUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = HeuristicBotUI(game_logic)
    game_ui.run()

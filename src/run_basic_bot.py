from core.game_logic import GameLogic
from ui.agents.heuristic.basic_bot_ui import BasicBotUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = BasicBotUI(game_logic)
    game_ui.run()

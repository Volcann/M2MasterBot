from core.game_logic import GameLogic
from ui.agents.heuristic.linear_bot_ui import LinearBotUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = LinearBotUI(game_logic)
    game_ui.run()

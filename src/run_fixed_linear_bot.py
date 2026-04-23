from core.game_logic import GameLogic
from ui.agents.heuristic.fixed_linear_bot_ui import FixedLinearBotUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = FixedLinearBotUI(game_logic)
    game_ui.run()

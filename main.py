from game_logic.game_logic import GameLogic
from game_ui.game_ui import GameUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = GameUI(game_logic)
    game_ui.run()

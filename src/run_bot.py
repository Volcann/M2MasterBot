from game_logic.game_logic import GameLogic
from M2Bot.game_bot_ui.game_bot_ui import BotGameUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = BotGameUI(game_logic)
    game_ui.run()

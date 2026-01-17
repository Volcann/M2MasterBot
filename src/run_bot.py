from core.game_logic import GameLogic
from ui.bot.game_bot_ui import BotGameUI

if __name__ == "__main__":
    game_logic = GameLogic()
    game_ui = BotGameUI(game_logic)
    game_ui.run()

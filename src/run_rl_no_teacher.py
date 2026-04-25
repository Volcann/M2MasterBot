from agents.rl.standard import NoTeacherAgent
from ui.agents.rl.rl_bot_ui import RLBotUI


class NoTeacherRLBotUI(RLBotUI):
    def __init__(self, model_path: str, move_interval_ms: int = 100, fps: int = 30):
        super().__init__(model_path, move_interval_ms, fps)
        self.agent = NoTeacherAgent()

    def load_agent(self):
        self.agent.load(self.model_path)

    def _select_action(self):
        return self.agent.select_action(
            self.game.get_matrix(), self.ui.next_value, epsilon=0.0
        )


if __name__ == "__main__":
    runner = NoTeacherRLBotUI(
        model_path="data/rl_no_teacher.json", move_interval_ms=100, fps=30
    )
    runner.run()

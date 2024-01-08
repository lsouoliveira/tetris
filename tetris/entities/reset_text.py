from tetris.config import Config
from tetris.entities.text import Text


class ResetText(Text):
    def __init__(self):
        super().__init__("PRESS SPACE TO RESTART", visible=False)
        self.blink_timer = 0
        self.blink_visible = False

    def update(self, dt):
        self.blink_timer += dt

        if self.blink_timer > Config.RESET_TEXT_INTERVAL:
            self.blink_visible = not self.blink_visible
            self.blink_timer = 0

    def draw(self, screen):
        if not self.blink_visible:
            return

        super().draw(screen)

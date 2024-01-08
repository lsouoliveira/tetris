from tetris.utils import draw_character
from tetris.config import Config


class Text:
    visible: bool
    text: str
    x: int
    y: int

    def __init__(self, text, visible=True):
        self.text = text
        self.visible = visible

    def draw(self, screen):
        if not self.visible:
            return

        draw_character(
            screen,
            self.y,
            self.x,
            self.text,
            Config.COLOR_GREEN,
        )

    def width(self):
        return len(self.text)

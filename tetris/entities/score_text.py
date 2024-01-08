from tetris.entities.text import Text
from tetris.utils import draw_character
from tetris.config import Config


class ScoreText(Text):
    def __init__(self, text, max_score_length=8):
        super().__init__(text, True)
        self.score = 0
        self.max_score_length = max_score_length

    def draw(self, screen):
        draw_character(
            screen,
            self.y,
            self.x,
            self.text + self.pad_empty_space() + str(self.score),
            Config.COLOR_GREEN,
        )

    def pad_empty_space(self):
        return " " * (self.max_score_length - len(str(self.score)))

    def width(self):
        return super().width() + self.max_score_length

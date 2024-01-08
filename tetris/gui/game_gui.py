import math


class GameGUI:
    def __init__(
        self,
        grid,
        score_text,
        game_over_text,
        next_piece,
        highest_score_text,
        reset_text,
    ):
        self.grid = grid
        self.score_text = score_text
        self.game_over_text = game_over_text
        self.next_piece = next_piece
        self.highest_score_text = highest_score_text
        self.reset_text = reset_text

    def update(self, dt):
        if self.next_piece is not None:
            self.next_piece.x = self.grid.x - 2 * self.next_piece.width() - 2
            self.next_piece.y = (
                self.grid.y
                + self.grid.height() // 2
                - math.ceil(self.next_piece.height() / 2)
            )

        self.score_text.x = self.grid.x - self.score_text.width() - 2
        self.score_text.y = self.grid.y + 1

        self.highest_score_text.x = self.grid.x - self.highest_score_text.width() - 2
        self.highest_score_text.y = self.grid.y

        self.game_over_text.x = (
            self.grid.x + self.grid.width() - self.game_over_text.width() // 2 + 2
        )
        self.game_over_text.y = self.grid.y + self.grid.height() // 2

        self.reset_text.x = (
            self.grid.x + self.grid.width() - self.reset_text.width() // 2 + 2
        )
        self.reset_text.y = self.grid.y + self.grid.height() + 4

        self.reset_text.update(dt)

    def draw(self, screen):
        self.grid.draw(screen)
        self.score_text.draw(screen)
        self.game_over_text.draw(screen)
        self.highest_score_text.draw(screen)
        self.reset_text.draw(screen)

        if self.next_piece is not None:
            self.next_piece.draw(screen)

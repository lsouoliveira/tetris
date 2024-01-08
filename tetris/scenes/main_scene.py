from __future__ import annotations
from enum import Enum, auto
import math
import time

from tetris.config import Config
from tetris.entities.grid import Grid
from tetris.entities.pieces import PieceFactory, PieceType
from tetris.entities.game_controller import GameController
from tetris.entities.score_text import ScoreText
from tetris.entities.reset_text import ResetText
from tetris.entities.text import Text
from tetris.gui.game_gui import GameGUI
from tetris.events import (
    Event,
    PieceAddedEvent,
    LinesClearedEvent,
    GameOverEvent,
)
from tetris.scenes.scene import Scene
from tetris.utils import calculate_score


class GameStatus(Enum):
    RUNNING = auto()
    GAME_OVER = auto()


class MainScene(Scene):
    def __init__(self, stdscr):
        super().__init__(stdscr)

    def init(self):
        self.piece_factory = PieceFactory()

        self.grid = Grid(Config.ROWS, Config.COLS, x=0, y=0)
        self.piece = self.piece_factory.create_piece(PieceType.I)
        self.next_piece = self.piece_factory.create_piece(PieceType.I)

        self.game_controller = GameController(self.grid, self.piece, self.stdscr)
        self.game_controller.add_observer(lambda event: self.on_event(event))
        self.game_controller.start()

        self.score = ScoreText("SCORE: ")
        self.highest_score_text = ScoreText("HIGHEST SCORE: ", max_score_length=8)
        self.game_over = Text("GAME OVER", visible=False)
        self.reset_text = ResetText()
        self.game_gui = GameGUI(
            self.grid,
            self.score,
            self.game_over,
            self.next_piece,
            self.highest_score_text,
            self.reset_text,
        )

        self.status = GameStatus.RUNNING

    def draw(self):
        self.game_gui.draw(self.stdscr)
        self.piece.draw(self.stdscr)

    def update(self, dt):
        self.game_gui.update(dt)
        self.game_controller.update(dt)

        if self.status == GameStatus.GAME_OVER:
            if self.stdscr.getch() == ord(" "):
                self.status = GameStatus.RUNNING
                self.game_controller.start()
                self.game_over.visible = False
                self.reset_text.visible = False

    def on_event(self, event: Event):
        if isinstance(event, PieceAddedEvent):
            self.next_piece.matrix = self.piece_factory.create_piece(
                event.piece_type
            ).matrix
            self.next_piece.x = self.grid.x - 2 * self.next_piece.width() - 2
            self.next_piece.y = (
                self.grid.y
                + self.grid.height() // 2
                - math.ceil(self.next_piece.height() / 2)
            )
        elif isinstance(event, GameOverEvent):
            self.status = GameStatus.GAME_OVER
            self.game_over.visible = True
            self.reset_text.visible = True

            if self.score.score > self.highest_score_text.score:
                self.highest_score_text.score = self.score.score
        elif isinstance(event, LinesClearedEvent):
            self.score.score += calculate_score(event.number_of_lines)

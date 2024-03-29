import random
import math

from tetris.events import (
    PieceAddedEvent,
    GameOverEvent,
    LinesClearedEvent,
)
from tetris.events import Observable
from tetris.entities.pieces import PieceFactory, POSSIBLE_PIECE_TYPES
from tetris.config import Config


class GameController(Observable):
    def __init__(self, grid, piece, stdscr):
        super().__init__()

        self.grid = grid
        self.piece = piece
        self.stdscr = stdscr
        self.piece_speed = Config.PIECE_SPEED
        self.piece_factory = PieceFactory()

    def start(self):
        self.lines_cleared = 0
        self.level = 1
        self.piece_speed = Config.PIECE_SPEED
        self.is_running = True
        self.can_move_piece_down = True
        self.piece_movement_timer = 0
        self.next_piece_type = None

        self.grid.initialize_grid(Config.ROWS, Config.COLS)
        self.centralize_grid()
        self.add_new_piece()

    def update(self, dt):
        self.centralize_grid()

        if not self.is_running:
            return

        self.handle_input()
        self.update_movement_timer(dt)

        if self.can_move_piece_down:
            if self.grid.can_place_piece_at(self.piece, self.piece.x, self.piece.y + 1):
                self.move_piece_down()
            else:
                self.grid.copy_piece_to_grid(self.piece)
                self.add_new_piece()
                if self.grid.are_any_rows_full():
                    removed_row_indexes = self.grid.remove_full_rows()
                    self.grid.shift_rows_down(removed_row_indexes)
                    self.lines_cleared += len(removed_row_indexes)
                    new_level = math.floor(self.lines_cleared / 10) + 1

                    if new_level > self.level:
                        self.handle_level_up(new_level)

                    self.notify_observers(LinesClearedEvent(len(removed_row_indexes)))

    def handle_level_up(self, new_level):
        self.level = new_level
        self.piece_speed += Config.PIECE_SPEED_INCREMENT

    def add_new_piece(self):
        new_piece_type = self.next_piece_type or random.choice(POSSIBLE_PIECE_TYPES)
        new_piece = self.piece_factory.create_piece(new_piece_type)
        self.next_piece_type = random.choice(POSSIBLE_PIECE_TYPES)

        self.piece.matrix = new_piece.matrix
        self.piece.x = (
            self.grid.x + self.grid.width() - math.ceil(self.piece.width() / 2)
        )
        self.piece.y = self.grid.y
        self.piece.reached_bottom = False
        self.piece_movement_timer = 0

        self.notify_observers(PieceAddedEvent(self.next_piece_type))

        if not self.grid.can_place_piece_at(self.piece, self.piece.x, self.piece.y):
            self.is_running = False
            self.notify_observers(GameOverEvent())

    def update_movement_timer(self, dt):
        self.piece_movement_timer += dt

        if self.piece_movement_timer > self.piece_speed:
            self.can_move_piece_down = True

    def move_piece_down(self):
        self.can_move_piece_down = False
        self.piece_movement_timer = 0
        self.piece.move_down()

    def centralize_grid(self):
        win_rows, win_cols = self.stdscr.getmaxyx()

        self.grid.x = (win_cols - 2 * Config.COLS - 2) // 2
        self.grid.y = (win_rows - Config.ROWS - 2) // 2

    def handle_input(self):
        key = self.stdscr.getch()

        if key == ord("l"):
            if self.grid.can_place_piece_at(self.piece, self.piece.x + 2, self.piece.y):
                self.piece.move_right()

        if key == ord("h"):
            if self.grid.can_place_piece_at(self.piece, self.piece.x - 2, self.piece.y):
                self.piece.move_left()

        if key == ord("i"):
            self.piece.rotate_clockwise()

            if not self.grid.can_place_piece_at(self.piece, self.piece.x, self.piece.y):
                self.piece.rotate_anticlockwise()

        if key == ord("z"):
            self.piece.rotate_anticlockwise()

            if not self.grid.can_place_piece_at(self.piece, self.piece.x, self.piece.y):
                self.piece.rotate_clockwise()

        if key == ord("j"):
            self.piece_speed = Config.FAST_PIECE_SPEED
        else:
            self.piece_speed = Config.PIECE_SPEED

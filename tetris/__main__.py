from typing import Optional
import curses
import time
from enum import Enum, auto
import random
import math

ROWS = 20
COLS = 10

COLOR_BLACK = 2
COLOR_GREEN = 1

EMPTY_CELL_ICON = " ·"

PIECE_SPEED = 0.25
FAST_PIECE_SPEED = 0.1

RESET_TEXT_INTERVAL = 0.5


def calculate_score(number_of_lines: int):
    if number_of_lines == 1:
        return 40

    if number_of_lines == 2:
        return 100

    if number_of_lines == 3:
        return 300

    return 1200


class PieceType(Enum):
    I = auto()
    O = auto()
    T = auto()
    S = auto()
    Z = auto()
    J = auto()
    L = auto()


POSSIBLE_PIECE_TYPES = [
    PieceType.I,
    PieceType.O,
    PieceType.T,
    PieceType.S,
    PieceType.Z,
    PieceType.J,
    PieceType.L,
]
PIECE_TYPE_SHAPES = {
    PieceType.I: [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
    ],
    PieceType.O: [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ],
    PieceType.T: [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0],
    ],
    PieceType.S: [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0],
    ],
    PieceType.Z: [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0],
    ],
    PieceType.J: [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0],
    ],
    PieceType.L: [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ],
}


def draw_character(screen, y, x, character, color):
    try:
        screen.addstr(y, x, character, curses.color_pair(color))
    except curses.error:
        pass


class Event:
    pass


class Observable:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event: Event):
        for observer in self.observers:
            observer(event)


class Cell:
    x: int
    y: int
    is_empty: bool

    def __init__(
        self,
        x: int,
        y: int,
        parent: Optional["Piece"],
        icon: str = "[]",
        is_empty: bool = False,
    ):
        self.x = x
        self.y = y
        self.parent = parent
        self.icon = icon
        self.is_empty = is_empty

    def draw(self, screen):
        draw_character(screen, self.y, self.x, self.icon, COLOR_GREEN)


class Piece:
    x: int
    y: int
    matrix: list[list[Cell]]
    grid: "Grid"
    rotatable: bool

    def __init__(self, matrix: list[list[Cell]], rotatable: bool = True):
        self.x = 0
        self.y = 0
        self.matrix = matrix
        self.reached_bottom = False
        self.rotatable = rotatable

    def draw(self, screen):
        for row_index, row in enumerate(self.matrix):
            for col_index, cell in enumerate(row):
                if cell is not None:
                    cell.x = self.x + col_index * 2
                    cell.y = self.y + row_index
                    cell.draw(screen)

    def width(self):
        return len(self.matrix[0])

    def height(self):
        return len(self.matrix)

    def move_right(self):
        self.x += 2

    def move_left(self):
        self.x -= 2

    def move_down(self):
        self.y += 1

    def rotate_clockwise(self):
        if not self.rotatable:
            return

        self.matrix = [
            list(map(lambda x: x[i], self.matrix))[::-1]
            for i in range(len(self.matrix[0]))
        ]

    def rotate_anticlockwise(self):
        if not self.rotatable:
            return

        self.matrix = [
            [self.matrix[j][i] for j in range(len(self.matrix))]
            for i in range(len(self.matrix[0]) - 1, -1, -1)
        ]


def build_piece_from_matrix(matrix: list[list[int]]) -> list[list[Cell]]:
    piece_matrix = []

    for i in range(len(matrix)):
        piece_matrix.append([])

        for j in range(len(matrix[i])):
            if matrix[i][j] == 1:
                piece_matrix[i].append(Cell(0, 0, None, is_empty=False))
            else:
                piece_matrix[i].append(None)

    return piece_matrix


class PieceFactory:
    def create_piece(self, piece_type: PieceType) -> Piece:
        return Piece(
            matrix=build_piece_from_matrix(PIECE_TYPE_SHAPES[piece_type]),
            rotatable=piece_type != PieceType.O,
        )


class Grid:
    grid: list[list[Cell]]
    x: int
    y: int
    rows: int
    cols: int

    def __init__(self, rows, cols, x, y):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.initialize_grid(rows, cols)

    def initialize_grid(self, rows, cols):
        self.grid = [
            [Cell(x, y, None, EMPTY_CELL_ICON, is_empty=True) for x in range(cols)]
            for y in range(rows)
        ]

    def draw(self, screen):
        for i in range(self.rows):
            draw_character(screen, self.y + i, self.x, "<!", COLOR_GREEN)
            draw_character(
                screen, self.y + i, self.x + 2 * self.cols + 2, "!>", COLOR_GREEN
            )

        draw_character(screen, self.y + self.rows, self.x, "<!", COLOR_GREEN)
        draw_character(
            screen,
            self.y + self.rows,
            self.x + 2 * self.cols + 2,
            "!>",
            COLOR_GREEN,
        )
        for i in range(2 * self.cols):
            draw_character(screen, self.y + self.rows, self.x + i + 2, "=", COLOR_GREEN)

        for i in range(self.cols):
            draw_character(
                screen, self.y + self.rows + 1, self.x + i * 2 + 2, "\\/", COLOR_GREEN
            )

        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if cell is not None:
                    cell.x = self.x + 2 * col_index + 2
                    cell.y = self.y + row_index
                    cell.draw(screen)

    def width(self):
        return self.cols

    def height(self):
        return self.rows

    def copy_piece_to_grid(self, piece: Piece):
        for row_index, row in enumerate(piece.matrix):
            for col_index, cell in enumerate(row):
                if cell is not None:
                    grid_x = (piece.x - self.x - 2) // 2
                    grid_y = piece.y - self.y

                    self.grid[grid_y + row_index][grid_x + col_index] = cell

    def can_place_piece_at(self, piece: Piece, x: int, y: int):
        grid_x = (x - 2 - self.x) // 2
        grid_y = y - self.y

        for row_index, row in enumerate(piece.matrix):
            for col_index, _ in enumerate(row):
                if piece.matrix[row_index][col_index] is None:
                    continue

                if grid_y + row_index < 0 or grid_y + row_index >= self.rows:
                    return False

                if grid_x + col_index < 0 or grid_x + col_index >= self.cols:
                    return False

                grid_cell = self.grid[grid_y + row_index][grid_x + col_index]

                if not grid_cell.is_empty:
                    return False

        return True

    def are_any_rows_full(self):
        for row in self.grid:
            if all([not cell.is_empty for cell in row]):
                return True

        return False

    def remove_full_rows(self):
        removed_rows = []

        for row_index, row in enumerate(self.grid):
            if self.is_row_full(row):
                self.grid[row_index] = [
                    Cell(0, 0, None, EMPTY_CELL_ICON, is_empty=True) for _ in row
                ]

                removed_rows.append(row_index)

        return removed_rows

    def shift_rows_down(self, rows: list[int]):
        for i, row_index in enumerate(rows):
            self.grid.pop(row_index - i)

        for _ in range(len(rows)):
            self.grid.insert(
                0,
                [
                    Cell(0, 0, None, EMPTY_CELL_ICON, is_empty=True)
                    for _ in range(self.cols)
                ],
            )

    def is_row_full(self, row):
        return all([not cell.is_empty for cell in row])

    def is_row_empty(self, row):
        return all([cell.is_empty for cell in row])


class PieceAddedEvent(Event):
    def __init__(self, piece_type: PieceType):
        self.piece_type = piece_type


class GameOverEvent(Event):
    pass


class LinesClearedEvent(Event):
    def __init__(self, number_of_lines: int):
        self.number_of_lines = number_of_lines


class GameController(Observable):
    def __init__(self, grid, piece, stdscr):
        super().__init__()

        self.grid = grid
        self.piece = piece
        self.stdscr = stdscr
        self.piece_speed = PIECE_SPEED
        self.piece_movement_timer = 0
        self.piece_factory = PieceFactory()
        self.can_move_piece_down = True
        self.is_running = True

    def start(self):
        self.is_running = True
        self.grid.initialize_grid(ROWS, COLS)
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
                    self.notify_observers(LinesClearedEvent(len(removed_row_indexes)))

    def add_new_piece(self):
        random_piece_type = random.choice(POSSIBLE_PIECE_TYPES)
        new_piece = self.piece_factory.create_piece(random_piece_type)

        self.piece.matrix = new_piece.matrix
        self.piece.x = (
            self.grid.x + self.grid.width() - math.ceil(self.piece.width() / 2)
        )
        self.piece.y = self.grid.y
        self.piece.reached_bottom = False
        self.piece_movement_timer = 0

        self.notify_observers(PieceAddedEvent(random_piece_type))

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

        self.grid.x = (win_cols - 2 * COLS - 2) // 2
        self.grid.y = (win_rows - ROWS - 2) // 2

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
            self.piece_speed = FAST_PIECE_SPEED
        else:
            self.piece_speed = PIECE_SPEED


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
            COLOR_GREEN,
        )

    def width(self):
        return len(self.text)


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
            COLOR_GREEN,
        )

    def pad_empty_space(self):
        return " " * (self.max_score_length - len(str(self.score)))

    def width(self):
        return super().width() + self.max_score_length


class ResetText(Text):
    def __init__(self):
        super().__init__("PRESS SPACE TO RESTART", visible=False)
        self.blink_timer = 0
        self.blink_visible = False

    def update(self, dt):
        self.blink_timer += dt

        if self.blink_timer > RESET_TEXT_INTERVAL:
            self.blink_visible = not self.blink_visible
            self.blink_timer = 0

    def draw(self, screen):
        if not self.blink_visible:
            return

        super().draw(screen)


class GameStatus(Enum):
    RUNNING = auto()
    GAME_OVER = auto()


class Game:
    def init(self):
        self.init_curses()

        self.last_time = time.time()
        self.piece_factory = PieceFactory()

        self.grid = Grid(ROWS, COLS, x=0, y=0)
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

    def run(self):
        while True:
            self.update()
            self.draw()

            time.sleep(1 / 60.0)

    def draw(self):
        self.clear_screen()

        self.game_gui.draw(self.stdscr)
        self.piece.draw(self.stdscr)

        self.stdscr.refresh()

    def update(self):
        dt = self.delta_time()

        self.game_gui.update(dt)

        self.game_controller.update(dt)

        if self.status == GameStatus.GAME_OVER:
            if self.stdscr.getch() == ord(" "):
                self.status = GameStatus.RUNNING
                self.game_controller.start()
                self.game_over.visible = False
                self.reset_text.visible = False

    def delta_time(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        return dt

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

    def init_curses(self):
        self.stdscr = curses.initscr()

        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        curses.start_color()

        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_color(0, 0, 0, 0)

    def clear_screen(self):
        self.stdscr.erase()
        self.stdscr.bkgd(" ", curses.color_pair(2))

    def exit(self):
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()


def main():
    game = Game()

    try:
        game.init()
        game.run()
    except KeyboardInterrupt:
        game.exit()


if __name__ == "__main__":
    main()

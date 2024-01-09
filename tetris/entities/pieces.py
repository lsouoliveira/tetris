from typing import Optional
from enum import Enum, auto

from tetris.utils import draw_character
from tetris.config import Config


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


def build_piece_from_matrix(matrix: list[list[int]]) -> list[list["Cell"]]:
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
    def create_piece(self, piece_type: "PieceType", rotation=0) -> "Piece":
        piece =  Piece(
            matrix=build_piece_from_matrix(PIECE_TYPE_SHAPES[piece_type]),
            rotatable=piece_type != PieceType.O,
        )

        for _ in range(rotation):
            piece.rotate_clockwise()

        return piece


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
        draw_character(screen, self.y, self.x, self.icon, Config.COLOR_GREEN)


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

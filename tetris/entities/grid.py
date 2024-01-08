from tetris.entities.pieces import Piece, Cell
from tetris.config import Config
from tetris.utils import draw_character


class Grid:
    grid: list[list["Cell"]]
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
            [
                Cell(x, y, None, Config.EMPTY_CELL_ICON, is_empty=True)
                for x in range(cols)
            ]
            for y in range(rows)
        ]

    def draw(self, screen):
        for i in range(self.rows):
            draw_character(screen, self.y + i, self.x, "<!", Config.COLOR_GREEN)
            draw_character(
                screen, self.y + i, self.x + 2 * self.cols + 2, "!>", Config.COLOR_GREEN
            )

        draw_character(screen, self.y + self.rows, self.x, "<!", Config.COLOR_GREEN)
        draw_character(
            screen,
            self.y + self.rows,
            self.x + 2 * self.cols + 2,
            "!>",
            Config.COLOR_GREEN,
        )
        for i in range(2 * self.cols):
            draw_character(
                screen, self.y + self.rows, self.x + i + 2, "=", Config.COLOR_GREEN
            )

        for i in range(self.cols):
            draw_character(
                screen,
                self.y + self.rows + 1,
                self.x + i * 2 + 2,
                "\\/",
                Config.COLOR_GREEN,
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
                    Cell(0, 0, None, Config.EMPTY_CELL_ICON, is_empty=True) for _ in row
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
                    Cell(0, 0, None, Config.EMPTY_CELL_ICON, is_empty=True)
                    for _ in range(self.cols)
                ],
            )

    def is_row_full(self, row):
        return all([not cell.is_empty for cell in row])

    def is_row_empty(self, row):
        return all([cell.is_empty for cell in row])

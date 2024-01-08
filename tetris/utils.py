import curses


def calculate_score(number_of_lines: int):
    if number_of_lines == 1:
        return 40

    if number_of_lines == 2:
        return 100

    if number_of_lines == 3:
        return 300

    return 1200


def draw_character(screen, y, x, character, color):
    try:
        screen.addstr(y, x, character, curses.color_pair(color))
    except curses.error:
        pass

import curses
import time

from tetris.scenes.main_scene import MainScene


class Game:
    def init(self):
        self.init_curses()

        self.last_time = time.time()
        self.main_scene = MainScene(self.stdscr)
        self.main_scene.init()

    def run(self):
        while True:
            self.update()
            self.draw()

            time.sleep(1 / 60.0)

    def draw(self):
        self.clear_screen()
        self.main_scene.draw()
        self.stdscr.refresh()

    def update(self):
        dt = self.delta_time()

        self.main_scene.update(dt)

    def delta_time(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        return dt

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

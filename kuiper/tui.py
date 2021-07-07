"""
Based on https://github.com/mingrammer/python-curses-scroll-example
License: https://github.com/mingrammer/python-curses-scroll-example/blob/master/LICENSE
"""

import curses
from curses import wrapper
from curses import ascii

sess = None


class TUI:
    UP = -1
    DOWN = 1

    def __init__(self, stdscr, items):
        self.window = stdscr
        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

        self.items = items

        self.max_lines = curses.LINES - 2
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

    def run(self):
        """Continue running the TUI until get interrupted"""
        try:
            self.input_stream()
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()

    def input_stream(self):
        """Waiting an input and run a proper method according to type of input"""
        while True:
            self.display()

            ch = self.window.getch()
            if ch == curses.KEY_UP:
                self.scroll(self.UP)
            elif ch == curses.KEY_DOWN:
                self.scroll(self.DOWN)
            elif ch == curses.KEY_LEFT:
                self.paging(self.UP)
            elif ch == curses.KEY_RIGHT:
                self.paging(self.DOWN)
            elif ch == curses.KEY_RESIZE:
                self.max_lines = self.window.getmaxyx()[0] - 2
                self.page = self.bottom // self.max_lines
            elif ch == ascii.ESC:
                break

    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.current + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            return
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        if (direction == self.DOWN) and (next_line == self.max_lines) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            return
        # Scroll up
        # current cursor position or top position is greater than 0
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            return
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.current = next_line
            return

    def paging(self, direction):
        """Paging the window when pressing left/right arrow keys"""
        current_page = (self.top + self.current) // self.max_lines
        next_page = current_page + direction
        # The last page may have fewer items than max lines,
        # so we should adjust the current cursor position as maximum item count on last page
        if next_page == self.page:
            self.current = min(self.current, self.bottom % self.max_lines - 1)

        # Page up
        # if current page is not a first page, page up is possible
        # top position can not be negative, so if top position is going to be negative, we should set it as 0
        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return
        # Page down
        # if current page is not a last page, page down is possible
        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return

    def display(self):
        """Display the items on window"""
        self.window.erase()
        self.window.box()

        for idx, item in enumerate(self.items[self.top:self.top + self.max_lines]):
            try:
                # Highlight the current cursor line
                if idx == self.current:
                    self.window.addstr(idx + 1, 2, item, curses.color_pair(2))
                else:
                    self.window.addstr(idx + 1, 1, item, curses.color_pair(1))
            except curses.error:
                # This occurs when there aren't enough terminal lines to render the requested items, happens
                # when users resize window too quickly
                continue
        self.window.refresh()


def main(stdscr):
    global sess

    tui = TUI(stdscr, [f"Line {i}" for i in range(1, 501)])

    tui.run()


def start_tui(session):
    global sess
    sess = session

    wrapper(main)

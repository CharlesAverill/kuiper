"""
Based on https://github.com/mingrammer/python-curses-scroll-example
License: https://github.com/mingrammer/python-curses-scroll-example/blob/master/LICENSE
"""

import curses

from curses import wrapper
from curses import ascii

from .views import *
from .input import *
from .states import WindowState, LoginState

sess = None


class TUI:
    UP = -1
    DOWN = 1

    def __init__(self, stdscr, state, sess, items):
        self.window = stdscr
        self.state = state
        self.sess = sess
        self.items = items

        self.sub_state = None

        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

        self.max_lines = curses.LINES - 2
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

        self.display_states = {
            WindowState.LOGIN: (vlogin, ilogin),
            WindowState.REGISTER: (vregister, iregister),
            WindowState.POSTS_VIEW: (vforum, iforum),
        }

        self.states_dicts = {
            WindowState.LOGIN: {
                LoginState.USERNAME: "username",
                LoginState.PASSWORD: "password",
                LoginState.LOGIN: None,
                LoginState.REGISTER: None
            },
            WindowState.REGISTER: {
                RegisterState.USERNAME: "username",
                RegisterState.EMAIL: "email",
                RegisterState.PASSWORD: "password",
                RegisterState.AGE: "age",
                RegisterState.MAJOR: "major",
                RegisterState.REGISTER: None,
                RegisterState.BACK_TO_LOGIN: None
            }
        }

        self.states_lists = {
            WindowState.LOGIN: [
                LoginState.USERNAME,
                LoginState.PASSWORD,
                LoginState.LOGIN,
                LoginState.REGISTER
            ],
            WindowState.REGISTER: [
                RegisterState.USERNAME,
                RegisterState.EMAIL,
                RegisterState.PASSWORD,
                RegisterState.AGE,
                RegisterState.MAJOR,
                RegisterState.REGISTER,
                RegisterState.BACK_TO_LOGIN
            ]
        }

        self.input_verification = ascii.isalnum
        self.max_input_len = None

        self.buffers = {}
        self.current_buf = ""
        self.reading_shorthand_input = False
        self.shorthand_input_password_mode = False
        self.flashing = None

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
            display_func, input_func = self.display_states[self.state]
            display_func(self)

            if self.flashing is not None:
                flash(self, self.flashing)

            ch = self.window.getch()
            unctrl = ascii.unctrl(ch)

            if self.flashing is not None and (ch == curses.KEY_ENTER or unctrl == "^J"):
                self.flashing = None
                continue

            if self.reading_shorthand_input and self.input_verification(ch):
                if self.max_input_len is None or (self.max_input_len is not None and len(self.current_buf) < self.max_input_len):
                    self.current_buf += unctrl
                else:
                    curses.beep()
            if ch == curses.KEY_BACKSPACE or unctrl == "^?":
                # Backspace
                self.current_buf = self.current_buf[:-1]

            if ch == ascii.ESC:
                break

            elif ch == curses.KEY_RESIZE:
                self.height, self.width = self.window.getmaxyx()
                self.max_lines = self.height - 2
                self.page = self.bottom // self.max_lines

            input_func(self, ch)

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

    def shorthand_input(self):
        self.window.addstr(self.max_lines,
                           1,
                           "$ " + (self.current_buf if not self.shorthand_input_password_mode else "*" * len(
                               self.current_buf)),
                           curses.color_pair(2))

    def update_items(self, new_items):
        self.items = new_items
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

    def update_state(self, new_state):
        self.input_verification = ascii.isalnum
        self.max_input_len = None

        self.buffers = {}
        self.current_buf = ""
        self.reading_shorthand_input = False
        self.shorthand_input_password_mode = False

        self.sub_state = None
        self.state = new_state


def main(stdscr):
    global sess

    state = WindowState.LOGIN
    tui = TUI(stdscr, state, sess, [f"Line {i}" for i in range(1, 501)])

    tui.run()


def start_tui(session):
    global sess
    sess = session

    wrapper(main)

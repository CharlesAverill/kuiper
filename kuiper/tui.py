"""
Based on https://github.com/mingrammer/python-curses-scroll-example
License: https://github.com/mingrammer/python-curses-scroll-example/blob/master/LICENSE
"""

import curses
import subprocess
import tempfile

from curses import wrapper, textpad
from curses import ascii

from enum import Enum

from . import __version__

sess = None


class WindowState(Enum):
    LOGIN = 1
    REGISTER = 2
    LOGOUT = 3

    POSTS_VIEW = 4
    NEW_POST_VIEW = 5

    ACCOUNT_DETAILS = 6


class LoginState(Enum):
    USERNAME = 1
    PASSWORD = 2
    LOGIN = 3
    REGISTER = 4


class TUI:
    UP = -1
    DOWN = 1

    def __init__(self, stdscr, state, items):
        self.window = stdscr
        self.state = state
        self.items = items

        self.login_state = LoginState.USERNAME

        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

        self.max_lines = curses.LINES - 2
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

        self.display_states = {
            WindowState.LOGIN: self.login_display,
            WindowState.POSTS_VIEW: self.forum_display
        }

        self.login_states_dict = {
            LoginState.USERNAME: "username",
            LoginState.PASSWORD: "password",
            LoginState.LOGIN: None,
            LoginState.REGISTER: None
        }

        self.login_states_list = [
            LoginState.USERNAME,
            LoginState.PASSWORD,
            LoginState.LOGIN,
            LoginState.REGISTER
        ]
        
        self.buffers = {}
        self.current_buf = ""
        self.reading_shorthand_input = False
        self.shorthand_input_password_mode = False

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
            display_func = self.display_states[self.state]
            display_func()

            ch = self.window.getch()
            unctrl = ascii.unctrl(ch)

            if self.state == WindowState.LOGIN:
                # Enable/disable shorthand/password input
                self.reading_shorthand_input = self.login_state in [LoginState.USERNAME, LoginState.PASSWORD]
                self.shorthand_input_password_mode = self.login_state == LoginState.PASSWORD

            if self.reading_shorthand_input and ascii.isalnum(ch):
                self.current_buf += unctrl

            if ch == ascii.ESC:
                break

            elif ch == curses.KEY_RESIZE:
                self.height, self.width = self.window.getmaxyx()
                self.max_lines = self.height - 2
                self.page = self.bottom // self.max_lines

            # Forum Page
            if self.state == WindowState.POSTS_VIEW:
                if ch == curses.KEY_UP:
                    self.scroll(self.UP)
                elif ch == curses.KEY_DOWN:
                    self.scroll(self.DOWN)
                elif ch == curses.KEY_LEFT:
                    self.paging(self.UP)
                elif ch == curses.KEY_RIGHT:
                    self.paging(self.DOWN)
            # Login Page
            elif self.state == WindowState.LOGIN:
                # Check for field changes, save to the buffers dictionary if changed, jump to next/prev field
                if ch == curses.KEY_UP:
                    self.buffers[self.login_state] = self.current_buf
                    self.login_state = self.login_states_list[self.login_states_list.index(self.login_state) - 1]
                    self.current_buf = self.buffers[self.login_state] if self.login_state in self.buffers.keys() else ""
                elif ch == curses.KEY_DOWN:
                    self.buffers[self.login_state] = self.current_buf
                    idx = self.login_states_list.index(self.login_state) + 1
                    self.login_state = self.login_states_list[0 if idx > len(self.login_states_list) - 1 else idx]
                    self.current_buf = self.buffers[self.login_state] if self.login_state in self.buffers.keys() else ""
                # Carriage Return
                if ch == curses.KEY_ENTER or unctrl == "^J":
                    # Login
                    if self.login_state == LoginState.LOGIN:
                        exit(f"Logging in: {self.buffers}")
                    # Go to registration
                    elif self.login_state == LoginState.REGISTER:
                        exit("Go to registration")
                    # Go to next field
                    else:
                        self.buffers[self.login_state] = self.current_buf
                        idx = self.login_states_list.index(self.login_state) + 1
                        self.login_state = self.login_states_list[
                            0 if idx > len(self.login_states_list) - 1 else idx]
                        self.current_buf = self.buffers[self.login_state] if self.login_state in self.buffers.keys() else ""
                # Backspace
                elif ch == curses.KEY_BACKSPACE or unctrl == "^?":
                    self.current_buf = self.current_buf[:-1]

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

    def add_center_string(self, window, string, voffset, color_pair_index=1):
        _, x = window.getmaxyx()
        # Clip string so it doesn't go out of bounds
        string = string[:x - 2]
        window.addstr(voffset, int((self.width / 2) - len(string) / 2), string, curses.color_pair(color_pair_index))

    def shorthand_input(self):
        self.window.addstr(self.max_lines,
                           1,
                           "$ " + (self.current_buf if not self.shorthand_input_password_mode else "*" * len(self.current_buf)),
                           curses.color_pair(2))

    def login_display(self):
        """Display login prompt"""
        self.window.erase()
        self.window.box()

        # Login Header
        self.add_center_string(self.window, f"Kuiper {__version__}", 1)
        self.add_center_string(self.window, "A terminal-based dating application for UTD Students", 2)
        self.add_center_string(self.window, "Charles Averill - charles.averill@utdallas.edu - "
                                            "https://github.com/CharlesAverill/kuiper", 3)

        # Username label and field
        color_pair = 2 if self.login_state == LoginState.USERNAME else 1
        if LoginState.USERNAME in self.buffers.keys():
            self.window.addstr(5, 13, self.buffers[LoginState.USERNAME], curses.color_pair(color_pair))
        self.window.addstr(5, 3, "Username:", curses.color_pair(color_pair))

        # Password label and field
        color_pair = 2 if self.login_state == LoginState.PASSWORD else 1
        if LoginState.PASSWORD in self.buffers.keys():
            self.window.addstr(6, 13, "*" * len(self.buffers[LoginState.PASSWORD]), curses.color_pair(color_pair))
        self.window.addstr(6, 3, "Password:", curses.color_pair(color_pair))

        # Login button
        self.window.addstr(8, 3, "Login", curses.color_pair(2 if self.login_state == LoginState.LOGIN else 1))

        # Register button
        self.window.addstr(9, 3, "Register", curses.color_pair(2 if self.login_state == LoginState.REGISTER else 1))

        self.reading_shorthand_input = self.login_state in [LoginState.USERNAME, LoginState.PASSWORD]
        self.shorthand_input_password_mode = self.login_state == LoginState.PASSWORD

        if self.reading_shorthand_input:
            self.shorthand_input()

        self.window.refresh()

    def forum_display(self):
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

    def update_items(self, new_items):
        self.items = new_items
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines


def main(stdscr):
    global sess

    state = WindowState.LOGIN
    tui = TUI(stdscr, state, [f"Line {i}" for i in range(1, 501)])

    tui.run()


def start_tui(session):
    global sess
    sess = session

    wrapper(main)

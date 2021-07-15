"""
Based on https://github.com/mingrammer/python-curses-scroll-example
License: https://github.com/mingrammer/python-curses-scroll-example/blob/master/LICENSE
"""

from curses import wrapper
from curses import ascii
import tempfile
import subprocess

from .views import *
from .input import *
from .states import WindowState, states_lists, states_dicts
from .utils import SuspendCurses


class TUI:
    UP = -3
    DOWN = 3

    def __init__(self, stdscr, state, client, cfg, user=None):
        self.window = stdscr
        self.state = state
        self.client = client
        self.cfg = cfg
        self.items = []
        self.posts = []
        self.reload_posts = True
        self.user = user

        self.sub_state = None

        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Normal text
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Highlighted text
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)  # Flash text
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Border stuff

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

        self.max_lines = curses.LINES - 5
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

        self.display_states = {
            WindowState.LOGIN: (vlogin, ilogin),
            WindowState.REGISTER: (vregister, iregister),
            WindowState.FORUM_VIEW: (vforum, iforum),
            WindowState.NEW_POST_VIEW: (vnew_post, inew_post),
            WindowState.ACCOUNT_MENU: (vaccount_menu, iaccount_menu)
        }

        self.states_lists = states_lists
        self.states_dicts = states_dicts

        self.input_verification = ascii.isalnum
        self.max_input_len = None

        self.buffers = {}
        self.current_buf = ""
        self.reading_shorthand_input = False
        self.shorthand_input_password_mode = False
        self.flashing = None

        self.min_width = 135
        self.min_height = 40

        self.reload_posts = False
        self.post_index = 0
        self.post_line_max = 10
        self.post_char_max = 80

        self.review_post_state = None
        self.post_title = ""
        self.post_lines = []

        self.user_cache = {}

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
            try:
                # Check terminal size and display error message if needed
                if self.height < self.min_height or self.width < self.min_width:
                    if self.window.getch() == ascii.ESC:
                        break

                    self.height, self.width = self.window.getmaxyx()
                    self.window.erase()
                    self.window.box()

                    self.flash(f"Terminal window too small. Minimum size is {self.min_width}x{self.min_height}",
                               no_enter=True)

                    self.window.refresh()

                    continue

                if self.reload_posts:
                    self.update_posts(self.client.get_all_posts())
                    self.reload_posts = False

                display_func, input_func = self.display_states[self.state]
                display_func(self)

                if self.flashing is not None:
                    self.flash(self.flashing)

                ch = self.window.getch()

                unctrl = curses.ascii.unctrl(ch)

                if self.flashing is not None:
                    if ch == curses.KEY_ENTER or unctrl == "^J":
                        self.flashing = None
                    continue

                if self.reading_shorthand_input and self.input_verification(ch):
                    if self.max_input_len is None or (
                            self.max_input_len is not None and len(self.current_buf) < self.max_input_len):
                        self.current_buf += unctrl
                    else:
                        curses.beep()

                if self.reading_shorthand_input and ch == curses.KEY_BACKSPACE or unctrl == "^?":
                    # Backspace
                    self.current_buf = self.current_buf[:-1]

                elif ch == ascii.ESC:
                    break

                elif ch == curses.KEY_RESIZE:
                    self.height, self.width = self.window.getmaxyx()
                    self.max_lines = self.height - 5
                    self.page = self.bottom // (self.max_lines + 1)

                    continue

                input_func(self, ch)
            except ConnectionRefusedError:
                TUI.flashing = "Cannot find host, please check your internet connection"

    def shift_sub_states(self, ch, up=True, down=True):
        # Check for field changes, save to the buffers dictionary if changed, jump to next/prev field
        state_list = self.states_lists[self.state]
        if up and ch == curses.KEY_UP:
            self.buffers[self.sub_state] = self.current_buf
            self.sub_state = state_list[state_list.index(self.sub_state) - 1]
            self.current_buf = self.buffers[self.sub_state] if self.sub_state in self.buffers.keys() else ""
        elif down and ch == curses.KEY_DOWN:
            self.buffers[self.sub_state] = self.current_buf
            idx = state_list.index(self.sub_state) + 1
            self.sub_state = state_list[0 if idx > len(state_list) - 1 else idx]
            self.current_buf = self.buffers[self.sub_state] if self.sub_state in self.buffers.keys() else ""

    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.current + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            self.post_index -= 1
            return
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        if (direction == self.DOWN) and (next_line == self.max_lines) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            self.post_index += 1
            return
        # Scroll up
        # current cursor position or top position is greater than 0
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            self.post_index -= 1
            return
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.current = next_line
            self.post_index += 1
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
        if (direction == int(self.UP / 3)) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return
        # Page down
        # if current page is not a last page, page down is possible
        if (direction == int(self.DOWN / 3)) and (current_page < self.page):
            self.top += self.max_lines
            return

    def shorthand_input(self):
        self.window.addstr(self.height - 2,
                           2,
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

        if new_state == WindowState.FORUM_VIEW:
            self.update_posts(self.client.get_all_posts())
            self.user_cache = {}

    def update_posts(self, new_posts):
        self.posts = new_posts
        items = []
        for post in self.posts:
            items.extend(str(post).split("\n"))
        self.update_items(items)

    def flash(self, message, color_pair_index=3, no_enter=False):
        y, x = self.window.getmaxyx()
        message = message[:x - 2]
        self.window.addstr(int(y / 2),
                           int((self.width / 2) - len(message) / 2),
                           message,
                           curses.color_pair(color_pair_index))
        if not no_enter:
            string = "Press Enter to continue"[:x - 2]
            self.window.addstr(int(y / 2) + 1,
                               int((self.width / 2) - len(string) / 2),
                               string,
                               curses.color_pair(color_pair_index))

    def add_center_string(self, string, y, max_x=None, min_x=0, color_pair_index=1):
        if max_x is None:
            max_x = self.width
        # Clip string so it doesn't go out of bounds
        string = string[:max_x - min_x - 2]
        self.window.addstr(y, int(((max_x + min_x) / 2) - len(string) / 2), string, curses.color_pair(color_pair_index))

    def get_from_text_editor(self):
        # Create a temporary file to write to
        tf = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
        tf_name = tf.name
        tf.close()

        try:
            # If modifying
            if len(self.post_lines) or len(self.post_title):
                with open(tf_name, "a") as tf_stream:
                    tf_stream.writelines([self.post_title] + self.post_lines)

            # Suspend TUI and open temporary file in cfg text editor
            with SuspendCurses():
                subprocess.call([self.cfg["text_editor"], tf_name])

            # Make sure our terminal looks good afterwards
            self.window.refresh()
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)

            # Read into post_lines
            with open(tf_name, "r") as tf_stream:
                self.post_lines = tf_stream.readlines()

            # Truncate lines and columns
            self.post_title = self.post_lines[0][:self.post_char_max]
            self.post_lines = [line[:self.post_char_max] for line in self.post_lines][1:self.post_line_max]

            return True
        except PermissionError:
            self.flashing = "Permission Error when booting text editor. Check your configs."
            return False
        except Exception:
            self.flashing = "Unknown Exception when booting text editor. Check your configs."
            return False


def main(stdscr, *args):
    """
    :param stdscr: Provided by curses.wrapper
    :param args: [Session, Client, Configs]
    """

    state = WindowState.LOGIN
    tui = TUI(stdscr, state, args[0], args[1])

    tui.run()


def start_tui(client, cfg):
    wrapper(main, client, cfg)

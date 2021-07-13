"""
Based on https://github.com/mingrammer/python-curses-scroll-example
License: https://github.com/mingrammer/python-curses-scroll-example/blob/master/LICENSE
"""

from curses import wrapper
from curses import ascii

from .views import *
from .input import *
from .states import WindowState, LoginState
from .utils import flash

from ..models import Post, User


class TUI:
    UP = -3
    DOWN = 3

    def __init__(self, stdscr, state, session, client, posts, cfg, user=None):
        self.window = stdscr
        self.state = state
        self.sess = session
        self.client = client
        self.cfg = cfg
        self.items = []
        self.posts = posts
        for post in self.posts:
            self.items.extend(str(post).split("\n"))
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
            WindowState.NEW_POST_VIEW: (vnew_post, inew_post)
        }

        self.states_dicts = {
            WindowState.LOGIN: {
                LoginState.USERNAME: "username",
                LoginState.PASSWORD: "password",
                LoginState.LOGIN: None,
                LoginState.REGISTER: None,
                LoginState.EXIT: None
            },
            WindowState.REGISTER: {
                RegisterState.USERNAME: "username",
                RegisterState.EMAIL: "email",
                RegisterState.PASSWORD: "password",
                RegisterState.AGE: "age",
                RegisterState.MAJOR: "major",
                RegisterState.REGISTER: None,
                RegisterState.BACK_TO_LOGIN: None
            },
            WindowState.NEW_POST_VIEW: {
                NewPostState.SUBMIT_POST: None,
                NewPostState.BACK_TO_VIM: None
            }
        }

        self.states_lists = {
            WindowState.LOGIN: [
                LoginState.USERNAME,
                LoginState.PASSWORD,
                LoginState.LOGIN,
                LoginState.REGISTER,
                LoginState.EXIT
            ],
            WindowState.REGISTER: [
                RegisterState.USERNAME,
                RegisterState.EMAIL,
                RegisterState.PASSWORD,
                RegisterState.AGE,
                RegisterState.MAJOR,
                RegisterState.REGISTER,
                RegisterState.BACK_TO_LOGIN
            ],
            WindowState.NEW_POST_VIEW: [
                NewPostState.SUBMIT_POST,
                NewPostState.BACK_TO_VIM
            ]
        }

        self.input_verification = ascii.isalnum
        self.max_input_len = None

        self.buffers = {}
        self.current_buf = ""
        self.reading_shorthand_input = False
        self.shorthand_input_password_mode = False
        self.flashing = None

        self.min_width = 135
        self.min_height = 40

        self.post_index = 0
        self.post_line_max = 10
        self.post_char_max = 80

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
            # Check terminal size and display error message if needed
            if self.height < self.min_height or self.width < self.min_width:
                if self.window.getch() == ascii.ESC:
                    break

                self.height, self.width = self.window.getmaxyx()
                self.window.erase()
                self.window.box()

                flash(self, f"Terminal window too small. Minimum size is {self.min_width}x{self.min_height}", no_enter=True)

                self.window.refresh()

                continue

            display_func, input_func = self.display_states[self.state]
            display_func(self)

            if self.flashing is not None:
                flash(self, self.flashing)

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


def generate_dummy_users_posts():
    users = []
    posts = []

    usernames = ["Charles", "Alan", "Tim", "Grace", "Ada", "Donald", "Dennis", "John", "Linus"]
    majors = ["Mech", "CS", "DS", "EE", "Business"]
    ages = [18, 19, 20, 21, 22]

    import random
    import datetime

    for i in range(50):
        u = User()
        u.username = random.choice(usernames)
        u.email = f"{u.username}@utdallas.edu"
        u.age = random.choice(ages)
        u.major = random.choice(majors)

        p = Post()
        p.title = f"Looking for a date {i}"
        p.content = f"""
            Hi all!\n
            My name is {u.username} and I'm looking for a date on XX/YY. I like blah and blah\n
            and blah as well.\n
            and this.\n
            80808080808080808080808080808080808080808080808080808080808080808080808080808end\n
            \n
            I really look forward to meeting y'all this year!\n
            \n
            Yours truly, \n
            {u.username}
            """
        p.user = u
        p.created_at = datetime.datetime(2021, 7, 8, random.randint(0, 23))

        users.append(u)
        posts.append(p)

    return users, posts


def main(stdscr, *args):
    """
    :param stdscr: Provided by curses.wrapper
    :param args: [Session, Client, Configs]
    """
    users, posts = generate_dummy_users_posts()

    state = WindowState.LOGIN
    tui = TUI(stdscr, state, args[0], args[1], posts, args[2])

    tui.run()


def start_tui(session, client, cfg):
    wrapper(main, session, client, cfg)

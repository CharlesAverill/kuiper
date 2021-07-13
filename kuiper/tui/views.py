import pkg_resources

from .states import *
from .utils import add_center_string

import curses
import math


def vlogin(TUI):
    """Display login prompt"""
    TUI.window.erase()
    TUI.window.box()

    if TUI.sub_state is None:
        TUI.sub_state = LoginState.USERNAME

    # Header
    add_center_string(TUI, f"Kuiper {pkg_resources.get_distribution('kuiper').version}", 1, color_pair_index=4)
    add_center_string(TUI, "A terminal-based dating application for UTD Students", 2, color_pair_index=4)
    add_center_string(TUI, "Charles Averill - charles.averill@utdallas.edu - "
                           "https://github.com/CharlesAverill/kuiper", 3, color_pair_index=4)

    # Username label and field
    color_pair = 2 if TUI.sub_state == LoginState.USERNAME else 1
    if LoginState.USERNAME in TUI.buffers.keys():
        TUI.window.addstr(5, 13, TUI.buffers[LoginState.USERNAME][:TUI.width - 14], curses.color_pair(color_pair))
    TUI.window.addstr(5, 3, "Username:", curses.color_pair(color_pair))

    # Password label and field
    color_pair = 2 if TUI.sub_state == LoginState.PASSWORD else 1
    if LoginState.PASSWORD in TUI.buffers.keys():
        TUI.window.addstr(6, 13, ("*" * len(TUI.buffers[LoginState.PASSWORD]))[:TUI.width - 14], curses.color_pair(color_pair))
    TUI.window.addstr(6, 3, "Password:", curses.color_pair(color_pair))

    # Login button
    TUI.window.addstr(8, 3, "Login", curses.color_pair(2 if TUI.sub_state == LoginState.LOGIN else 1))

    # Register button
    TUI.window.addstr(9, 3, "Register", curses.color_pair(2 if TUI.sub_state == LoginState.REGISTER else 1))

    # Exit button
    TUI.window.addstr(11, 3, "Exit", curses.color_pair(2 if TUI.sub_state == LoginState.EXIT else 1))

    TUI.reading_shorthand_input = TUI.sub_state in [LoginState.USERNAME, LoginState.PASSWORD]
    TUI.shorthand_input_password_mode = TUI.sub_state == LoginState.PASSWORD

    if TUI.reading_shorthand_input:
        TUI.shorthand_input()

    TUI.window.refresh()


def vregister(TUI):
    """Display register prompt"""
    TUI.window.erase()
    TUI.window.box()

    if TUI.sub_state is None:
        TUI.sub_state = RegisterState.USERNAME

    # Header
    add_center_string(TUI, "Register", 1, color_pair_index=4)

    # Username label and field
    color_pair = 2 if TUI.sub_state == RegisterState.USERNAME else 1
    if RegisterState.USERNAME in TUI.buffers.keys():
        TUI.window.addstr(4, 13, TUI.buffers[RegisterState.USERNAME], curses.color_pair(color_pair))
    TUI.window.addstr(4, 3, "Username:", curses.color_pair(color_pair))

    # Email label and field
    color_pair = 2 if TUI.sub_state == RegisterState.EMAIL else 1
    if RegisterState.EMAIL in TUI.buffers.keys():
        TUI.window.addstr(5, 15, TUI.buffers[RegisterState.EMAIL], curses.color_pair(color_pair))
    TUI.window.addstr(5, 3, "UTD E-Mail:", curses.color_pair(color_pair))

    # Password label and field
    color_pair = 2 if TUI.sub_state == RegisterState.PASSWORD else 1
    if RegisterState.PASSWORD in TUI.buffers.keys():
        TUI.window.addstr(6, 13, "*" * len(TUI.buffers[RegisterState.PASSWORD]), curses.color_pair(color_pair))
    TUI.window.addstr(6, 3, "Password:", curses.color_pair(color_pair))

    # Age label and field
    color_pair = 2 if TUI.sub_state == RegisterState.AGE else 1
    if RegisterState.AGE in TUI.buffers.keys():
        TUI.window.addstr(8, 8, TUI.buffers[RegisterState.AGE], curses.color_pair(color_pair))
    TUI.window.addstr(8, 3, "Age:", curses.color_pair(color_pair))

    # Major label and field
    color_pair = 2 if TUI.sub_state == RegisterState.MAJOR else 1
    if RegisterState.MAJOR in TUI.buffers.keys():
        TUI.window.addstr(9, 10, TUI.buffers[RegisterState.MAJOR], curses.color_pair(color_pair))
    TUI.window.addstr(9, 3, "Major:", curses.color_pair(color_pair))

    # Register button
    TUI.window.addstr(11, 3, "Register", curses.color_pair(2 if TUI.sub_state == RegisterState.REGISTER else 1))

    # Back to Login screen
    TUI.window.addstr(12, 3, "Back to Login",
                      curses.color_pair(2 if TUI.sub_state == RegisterState.BACK_TO_LOGIN else 1))

    TUI.reading_shorthand_input = TUI.sub_state not in [RegisterState.REGISTER, RegisterState.BACK_TO_LOGIN]
    TUI.shorthand_input_password_mode = TUI.sub_state == RegisterState.PASSWORD

    if TUI.reading_shorthand_input:
        TUI.shorthand_input()

    TUI.window.refresh()


def vforum(TUI):
    """Display the forum"""
    TUI.window.erase()
    TUI.window.box()

    # Set up structure
    vert = "│"
    horz = "─"
    topi = "┬"
    boti = "┴"
    riti = "┤"
    lfti = "├"

    # 20% Line
    border_20_percent = int(math.floor(TUI.width * .3))

    for idx in range(TUI.height - 2):
        if idx == 0:
            # Top intersection character
            border_20_percent_char = topi
            offset = -1
            TUI.window.addstr(idx + 1, border_20_percent, vert, curses.color_pair(4))
        elif idx == TUI.height - 3:
            # Bottom intersection character
            border_20_percent_char = boti
            offset = 1
            TUI.window.addstr(idx + 1, border_20_percent, vert, curses.color_pair(4))
        else:
            # Plain vertical character
            border_20_percent_char = vert
            offset = 0
        TUI.window.addstr(idx + 1 + offset, border_20_percent, border_20_percent_char, curses.color_pair(4))

    # Posts Header
    add_center_string(TUI, "Posts", 1, border_20_percent, color_pair_index=4)
    TUI.window.addstr(2, 0, lfti + horz * (border_20_percent - 1) + riti, curses.color_pair(4))

    # Content / Comments splitter
    TUI.window.addstr(int(TUI.height / 2),
                      border_20_percent,
                      lfti + horz * (TUI.width - border_20_percent - 2) + riti,
                      curses.color_pair(4))
    add_center_string(TUI, "Comments", int(TUI.height / 2) + 1, min_x=border_20_percent, color_pair_index=4)

    # List of posts
    for idx, item in enumerate(TUI.items[TUI.top:TUI.top + TUI.max_lines]):
        # Highlight the current cursor line
        border_offset = 2 if TUI.current <= idx <= TUI.current + 2 else 1
        TUI.window.addstr(idx + 4, border_offset, item[:border_20_percent - border_offset], curses.color_pair(border_offset))
        # Draw separators
        if idx % 3 == 0:
            dashes = horz * (border_20_percent - len(item) - border_offset) + riti
            if len(dashes) == 1:
                dashes = ""
            TUI.window.addstr(idx + 4, len(item) + border_offset, dashes, curses.color_pair(4))

    # Post contents
    current_post = TUI.posts[TUI.post_index]

    add_center_string(TUI, f"\"{current_post.title}\"", 1, min_x=border_20_percent, color_pair_index=1)

    label_start = border_20_percent + 2
    field_start = border_20_percent + 13

    TUI.window.addstr(2, label_start, "Username:  ", curses.color_pair(4))
    TUI.window.addstr(2, field_start, current_post.user.username[:TUI.width - field_start - 1], curses.color_pair(1))
    TUI.window.addstr(3, label_start, "Major:     ", curses.color_pair(4))
    TUI.window.addstr(3, field_start, current_post.user.major[:TUI.width - field_start - 1], curses.color_pair(1))
    TUI.window.addstr(4, label_start, "Time Left: ", curses.color_pair(4))
    TUI.window.addstr(4, field_start, current_post.time_left[:TUI.width - field_start - 1], curses.color_pair(1))

    for idx, line in enumerate(current_post.content.strip().split("\n")[::2]):
        if 6 + idx < int(TUI.height / 2):
            TUI.window.addstr(6 + idx, field_start, line.strip()[:TUI.width - border_20_percent - 13], curses.color_pair(1))

    # Command bar (spread across comments section bottom)
    commands = ["ENTER = Select", "n = New Post", "a = Account Menu",
                "p = View My Post", "l = Logout", "h = Help", "ESC = exit"]
    commands_len = len("".join(commands))
    n_whitespace_chars = int((TUI.width - border_20_percent - commands_len) / len(commands)) - 1
    commands_string = (" " + " " * n_whitespace_chars).join(commands)[:TUI.width - border_20_percent - 2]
    add_center_string(TUI, commands_string, TUI.height - 2, min_x=border_20_percent, color_pair_index=4)

    TUI.window.refresh()


def vnew_post(TUI):
    """Display the new post prompt"""
    TUI.window.erase()
    TUI.window.box()

    quarter_height = max(2, int(TUI.height / 8))

    add_center_string(TUI, "New Post", 1, color_pair_index=4)

    if TUI.state == NewPostState.WAIT_FOR_VIM:
        add_center_string(TUI, "VIM will be opened for post creation", quarter_height)

        add_center_string(TUI, f"The character-per-line limit is {TUI.post_char_max}", quarter_height + 2)
        add_center_string(TUI, "Characters above this limit will be truncated", quarter_height + 3)

        add_center_string(TUI, f"The lines-per-post limit is {TUI.post_line_max}", quarter_height + 5)
        add_center_string(TUI, "Lines above this limit will be truncated", quarter_height + 6)

        add_center_string(TUI, "Press Enter to launch VIM", int(TUI.height / 2), color_pair_index=4)
    elif TUI.state == NewPostState.REVIEW_POST:
        exit("Review Post")

    TUI.window.refresh()

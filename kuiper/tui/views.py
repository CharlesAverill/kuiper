from .states import *

from .. import __version__
from ..models import User

import curses
import curses.ascii
import math


def vlogin(TUI):
    """Display login prompt"""
    TUI.window.erase()
    TUI.window.box()

    if TUI.sub_state is None:
        TUI.sub_state = LoginState.USERNAME

    # Header
    TUI.add_center_string(f"Kuiper {__version__}", 1, color_pair_index=4)
    TUI.add_center_string(f"A terminal-based dating application for {TUI.cfg['org_name']} Members", 2,
                          color_pair_index=4)
    TUI.add_center_string("Charles Averill - charles.averill@utdallas.edu - "
                          "https://github.com/CharlesAverill/kuiper", 3, color_pair_index=4)

    # Username label and field
    color_pair = 2 if TUI.sub_state == LoginState.USERNAME else 1
    if LoginState.USERNAME in TUI.buffers.keys():
        TUI.window.addstr(5, 13, TUI.buffers[LoginState.USERNAME][:TUI.width - 14], curses.color_pair(color_pair))
    TUI.window.addstr(5, 3, "Username:", curses.color_pair(color_pair))

    # Password label and field
    color_pair = 2 if TUI.sub_state == LoginState.PASSWORD else 1
    if LoginState.PASSWORD in TUI.buffers.keys():
        TUI.window.addstr(6, 13, ("*" * len(TUI.buffers[LoginState.PASSWORD]))[:TUI.width - 14],
                          curses.color_pair(color_pair))
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

    TUI.input_verification = curses.ascii.isalnum

    TUI.window.refresh()


def vregister(TUI):
    """Display register prompt"""
    TUI.window.erase()
    TUI.window.box()

    if TUI.sub_state is None:
        TUI.sub_state = RegisterState.USERNAME

    # Header
    TUI.add_center_string("Register", 1, color_pair_index=4)

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
    TUI.window.addstr(11, 3,
                      "Register" if not TUI.waiting_for_continue_registration else "Submit Registration Code",
                      curses.color_pair(2 if TUI.sub_state == RegisterState.REGISTER else 1))

    # Registration Code label and field
    color_pair = 2 if TUI.sub_state == RegisterState.REGISTRATION_CODE else 1
    if RegisterState.REGISTRATION_CODE in TUI.buffers.keys():
        TUI.window.addstr(12, 25, TUI.buffers[RegisterState.REGISTRATION_CODE], curses.color_pair(color_pair))
    TUI.window.addstr(12, 3, "Registration Code:", curses.color_pair(color_pair))

    # Back to Login screen
    TUI.window.addstr(14, 3, "Back to Login",
                      curses.color_pair(2 if TUI.sub_state == RegisterState.BACK_TO_LOGIN else 1))

    TUI.reading_shorthand_input = TUI.sub_state in [RegisterState.USERNAME,
                                                    RegisterState.PASSWORD,
                                                    RegisterState.EMAIL,
                                                    RegisterState.AGE,
                                                    RegisterState.MAJOR,
                                                    RegisterState.REGISTRATION_CODE]
    TUI.shorthand_input_password_mode = TUI.sub_state == RegisterState.PASSWORD

    if TUI.reading_shorthand_input:
        TUI.shorthand_input()

    if TUI.sub_state == RegisterState.AGE:
        TUI.max_input_len = 2
        TUI.input_verification = curses.ascii.isdigit
    elif TUI.sub_state == RegisterState.EMAIL:
        TUI.max_input_len = 40
        TUI.input_verification = curses.ascii.isprint
    else:
        TUI.max_input_len = 20

        def alnum_plus_space(c):
            return curses.ascii.unctrl(c) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

        TUI.input_verification = alnum_plus_space

    TUI.window.refresh()


def vforum(TUI):
    """Display the forum"""
    TUI.window.erase()
    TUI.window.box()

    # Set up structure
    vert = "???"
    horz = "???"
    topi = "???"
    boti = "???"
    riti = "???"
    lfti = "???"

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
    TUI.add_center_string("Posts", 1, border_20_percent, color_pair_index=4)
    TUI.window.addstr(2, 0, lfti + horz * (border_20_percent - 1) + riti, curses.color_pair(4))

    # Content / Comments splitter
    TUI.window.addstr(int(TUI.height / 2),
                      border_20_percent,
                      lfti + horz * (TUI.width - border_20_percent - 2) + riti,
                      curses.color_pair(4))
    TUI.add_center_string("Comments", int(TUI.height / 2) + 1, min_x=border_20_percent, color_pair_index=4)

    if TUI.posts:
        # List of posts
        temp = TUI.top + TUI.max_lines
        while temp % 3 != 0:
            temp -= 1
        for idx, item in enumerate(TUI.items[TUI.top:temp]):
            # Highlight the current cursor line
            border_offset = 2 if TUI.current <= idx <= TUI.current + 2 else 1
            TUI.window.addstr(idx + 4, border_offset, item[:border_20_percent - border_offset],
                              curses.color_pair(border_offset))
            # Draw separators
            if idx % 3 == 0:
                dashes = horz * (border_20_percent - len(item) - border_offset) + riti
                if len(dashes) == 1:
                    dashes = ""
                TUI.window.addstr(idx + 4, len(item) + border_offset, dashes, curses.color_pair(4))

        # Post contents
        if TUI.post_index >= len(TUI.posts) or TUI.post_index < 0:
            TUI.post_index = len(TUI.psots) - 1
        current_post = TUI.posts[TUI.post_index]

        TUI.add_center_string(f"\"{current_post.title}\"", 1, min_x=border_20_percent, color_pair_index=1)

        label_start = border_20_percent + 2
        field_start = border_20_percent + 13

        if current_post.user_username in TUI.user_cache:
            user = TUI.user_cache[current_post.user_username]
        else:
            user = User()
            user.from_json(TUI.client.get_user_by_username(current_post.user_username))
            TUI.user_cache.update({current_post.user_username: user})

        if user:
            TUI.window.addstr(2, label_start, "Username:  ", curses.color_pair(4))
            TUI.window.addstr(2, field_start, user.username[:TUI.width - field_start - 1], curses.color_pair(1))
            TUI.window.addstr(3, label_start, "Major:     ", curses.color_pair(4))
            TUI.window.addstr(3, field_start, user.major[:TUI.width - field_start - 1], curses.color_pair(1))
            TUI.window.addstr(4, label_start, "Time Left: ", curses.color_pair(4))
            TUI.window.addstr(4, field_start, current_post.time_left[:TUI.width - field_start - 1],
                              curses.color_pair(1))

            for idx, line in enumerate(current_post.content.strip().split("\n")):
                if 6 + idx < int(TUI.height / 2):
                    TUI.window.addstr(6 + idx, field_start, line.strip()[:TUI.width - border_20_percent - 13],
                                      curses.color_pair(1))
            # exit(current_post.content.strip().split("\n")[::2])
        else:
            TUI.add_center_string("Couldn't track down the user for this post", 1, min_x=border_20_percent)
    else:
        TUI.add_center_string("Hmmm. Either a slow day or your connection is down!", 1, min_x=border_20_percent,
                              color_pair_index=4)

    # Command bar (spread across comments section bottom)
    commands = ["ENTER = View User", "[r]eload Feed", "[n]ew Post",
                "[a]ccount Menu", "[l]ogout", "[h]elp", "ESC = exit"]
    commands_len = len("".join(commands))
    n_whitespace_chars = int((TUI.width - border_20_percent - commands_len) / len(commands)) - 1
    commands_string = (" " + " " * n_whitespace_chars).join(commands)[:TUI.width - border_20_percent - 2]
    TUI.add_center_string(commands_string, TUI.height - 2, min_x=border_20_percent, color_pair_index=4)

    TUI.window.refresh()


def vnew_post(TUI):
    """Display the new post prompt"""
    TUI.window.erase()
    TUI.window.box()

    if TUI.sub_state is None:
        TUI.sub_state = NewPostState.WAIT_FOR_VIM

    quarter_height = max(2, int(TUI.height / 8))
    half_height = int(TUI.height / 2)

    if TUI.sub_state == NewPostState.WAIT_FOR_VIM:
        TUI.add_center_string("New Post", 1, color_pair_index=4)

        TUI.add_center_string(f"{TUI.cfg['text_editor']} will be opened for post creation", quarter_height)
        TUI.add_center_string("Check your configs if this is not your preferred text editor", quarter_height + 1)

        TUI.add_center_string("The first line you type will be your post's title", quarter_height + 3)

        TUI.add_center_string(f"The character-per-line limit is {TUI.post_char_max}", quarter_height + 5)
        TUI.add_center_string("Characters above this limit will be truncated", quarter_height + 6)

        TUI.add_center_string(f"The lines-per-post limit is {TUI.post_line_max}", quarter_height + 8)
        TUI.add_center_string("Lines above this limit will be truncated", quarter_height + 9)

        TUI.add_center_string(f"Press Enter to launch {TUI.cfg['text_editor']}", half_height,
                              color_pair_index=4)
        TUI.add_center_string("Or, press Backspace to go back to the forum", half_height + 1,
                              color_pair_index=4)
    elif TUI.sub_state == NewPostState.REVIEW_POST:
        quarter_width = int(TUI.width / 4)

        TUI.add_center_string("Review Post", 1, color_pair_index=4)

        TUI.window.addstr(5, quarter_width, "Title:", curses.color_pair(4))
        TUI.window.addstr(5, quarter_width + 9, TUI.post_title, curses.color_pair(1))

        TUI.window.addstr(7, quarter_width, "Content:", curses.color_pair(4))
        idx = 0
        for idx, line in enumerate(TUI.post_lines):
            TUI.window.addstr(7 + idx, quarter_width + 9, line, curses.color_pair(1))

        TUI.window.addstr(7 + idx + 2,
                          quarter_width + 9,
                          "[s]ubmit",
                          curses.color_pair(2))

        TUI.window.addstr(8 + idx + 2,
                          quarter_width + 9,
                          "[m]odify",
                          curses.color_pair(2))

        # Redraw box because some weird stuff happens after subprocess
        TUI.window.box()
    elif TUI.sub_state == NewPostState.SUBMITTED:
        TUI.add_center_string("Post submitted!", half_height)
        TUI.add_center_string("Press Enter to go back to the Forum", half_height + 1)

    TUI.window.refresh()


def vaccount_menu(TUI):
    """Display account menu"""
    TUI.window.erase()
    TUI.window.box()

    if TUI.sub_state is None:
        TUI.sub_state = AccountMenuState.USERNAME

    # Header
    TUI.add_center_string("Account Menu", 1, color_pair_index=4)

    # Username label and field
    color_pair = 2 if TUI.sub_state == AccountMenuState.USERNAME else 1
    if AccountMenuState.USERNAME in TUI.buffers.keys():
        TUI.window.addstr(5, 13, TUI.buffers[AccountMenuState.USERNAME][:TUI.width - 14], curses.color_pair(color_pair))
    TUI.window.addstr(5, 3, "Username:", curses.color_pair(color_pair))

    # Age label and field
    color_pair = 2 if TUI.sub_state == AccountMenuState.AGE else 1
    if AccountMenuState.AGE in TUI.buffers.keys():
        TUI.window.addstr(6, 13, TUI.buffers[AccountMenuState.AGE][:TUI.width - 14], curses.color_pair(color_pair))
    TUI.window.addstr(6, 3, "Age:", curses.color_pair(color_pair))

    # Major label and field
    color_pair = 2 if TUI.sub_state == AccountMenuState.MAJOR else 1
    if AccountMenuState.MAJOR in TUI.buffers.keys():
        TUI.window.addstr(7, 13, TUI.buffers[AccountMenuState.MAJOR][:TUI.width - 14], curses.color_pair(color_pair))
    TUI.window.addstr(7, 3, "Major:", curses.color_pair(color_pair))

    # Password label and field
    color_pair = 2 if TUI.sub_state == AccountMenuState.RESET_PASSWORD else 1
    if AccountMenuState.RESET_PASSWORD in TUI.buffers.keys():
        TUI.window.addstr(9, 21, ("*" * len(TUI.buffers[AccountMenuState.RESET_PASSWORD]))[:TUI.width - 14],
                          curses.color_pair(color_pair))
    TUI.window.addstr(9, 3, "Reset Password:", curses.color_pair(color_pair))

    # Confirm Password label and field
    color_pair = 2 if TUI.sub_state == AccountMenuState.CONFIRM_PASSWORD else 1
    if AccountMenuState.CONFIRM_PASSWORD in TUI.buffers.keys():
        TUI.window.addstr(10, 21, ("*" * len(TUI.buffers[AccountMenuState.CONFIRM_PASSWORD]))[:TUI.width - 14],
                          curses.color_pair(color_pair))
    TUI.window.addstr(10, 3, "Confirm Password:", curses.color_pair(color_pair))

    # Submit Updates button
    TUI.window.addstr(12, 3, "Submit Profile Updates",
                      curses.color_pair(2 if TUI.sub_state == AccountMenuState.SUBMIT_UPDATES else 1))

    # View My Post button
    TUI.window.addstr(14, 3, "View My Post", curses.color_pair(2 if TUI.sub_state == AccountMenuState.VIEW_MY_POST
                                                               else 1))

    # Delete My Post button
    TUI.window.addstr(15, 3, "Delete My Post", curses.color_pair(2 if TUI.sub_state == AccountMenuState.DELETE_MY_POST
                                                                 else 1))

    # Back To Forum button
    TUI.window.addstr(17, 3, "Back to Forum", curses.color_pair(2 if TUI.sub_state == AccountMenuState.BACK_TO_FORUM
                                                                else 1))

    TUI.reading_shorthand_input = TUI.sub_state in [AccountMenuState.USERNAME,
                                                    AccountMenuState.RESET_PASSWORD,
                                                    AccountMenuState.AGE,
                                                    AccountMenuState.MAJOR,
                                                    AccountMenuState.CONFIRM_PASSWORD]
    TUI.shorthand_input_password_mode = TUI.sub_state in [AccountMenuState.CONFIRM_PASSWORD,
                                                          AccountMenuState.RESET_PASSWORD]

    if TUI.reading_shorthand_input:
        TUI.shorthand_input()

    TUI.input_verification = curses.ascii.isalnum

    TUI.window.refresh()


def vhelp(TUI):
    """Display account menu"""
    TUI.window.erase()
    TUI.window.box()

    TUI.add_center_string("Help Menu", 1, color_pair_index=4)

    TUI.window.addstr(3, 3, "How do I navigate?", curses.color_pair(4))
    TUI.window.addstr(3, 22, "Menu navigation is performed with the up and down arrow keys. "
                             "The forum view has hotkeys listed at the bottom", curses.color_pair(1))
    TUI.window.addstr(4, 22, " of the screen. For example, \"[l]ogout\" denotes that the \"l\" key logs you out.",
                      curses.color_pair(1))

    TUI.window.addstr(6, 3, "How do I exit the program?", curses.color_pair(4))
    TUI.window.addstr(6, 30, "The ESC key will completely exit the client on every menu", curses.color_pair(1))

    TUI.window.addstr(8, 3, "Are there any command line options?", curses.color_pair(4))
    TUI.window.addstr(8, 39, "Yes, run", curses.color_pair(1))
    TUI.window.addstr(8, 48, "kuiper -h", curses.color_pair(2))
    TUI.window.addstr(8, 58, "to view command line options and their descriptions", curses.color_pair(1))

    TUI.window.addstr(10, 3, "How do I request a feature or report a bug?", curses.color_pair(4))
    TUI.window.addstr(10, 47, "Visit https://github.com/CharlesAverill/kuiper/issues/new "
                              "to submit a new issue", curses.color_pair(1))
    TUI.window.addstr(11, 47, "with the tag \"enhancement\"", curses.color_pair(1))

    TUI.window.addstr(13, 3, "How do I support the project?", curses.color_pair(4))
    TUI.window.addstr(13, 33, "If you'd like to support the project, please consider contributing to the codebase!",
                      curses.color_pair(1))
    TUI.window.addstr(14, 33, "Otherwise, if you'd like to buy me a coffee or pay for some server time, email me!",
                      curses.color_pair(1))

    TUI.add_center_string("Press any key to return to the Forum", TUI.height - 2, color_pair_index=4)

    TUI.window.refresh()

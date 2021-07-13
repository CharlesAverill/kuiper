import curses
import re

from .states import RegisterState, LoginState


def validate_email(email, cfg):
    return re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    email) and email.endswith(cfg["required_email_suffix"])


def validate_number(num):
    try:
        x = int(num)
        return x
    except ValueError as e:
        return False


def validate_user_registration(vals, client, cfg):
    for key, value in zip(vals.keys(), vals.values()):
        if len(value) == 0 and key not in (RegisterState.REGISTER, RegisterState.BACK_TO_LOGIN):
            return "All fields are mandatory"
    if not validate_email(vals[RegisterState.EMAIL], cfg):
        return "Email is not valid"
    if len(vals[RegisterState.USERNAME]) < 5:
        return "Username must be at least 5 characters and end in '@utdallas.edu'"
    if len(vals[RegisterState.PASSWORD]) < 5:
        return "Password must be at least 5 characters"
    age = validate_number(vals[RegisterState.AGE])
    if age is False or (age is not False and not 17 < age < 100):
        return "Age must be on [17, 100]"
    if len(vals[RegisterState.MAJOR]) < 2:
        return "Major must be at least 2 characters"

    if client.get_user_by_email(vals[RegisterState.EMAIL]):
        return "Email already taken"

    if client.get_user_by_username(vals[RegisterState.USERNAME]):
        return "Username already taken"

    return "valid"


def validate_login(vals):
    for key, value in zip(vals.keys(), vals.values()):
        if len(value) == 0 and key not in (LoginState.REGISTER, LoginState.LOGIN):
            return True


def add_center_string(TUI, string, y, max_x=None, min_x=0, color_pair_index=1):
    if max_x is None:
        max_x = TUI.width
    # Clip string so it doesn't go out of bounds
    string = string[:max_x - min_x - 2]
    TUI.window.addstr(y, int(((max_x + min_x) / 2) - len(string) / 2), string, curses.color_pair(color_pair_index))


def flash(TUI, message, color_pair_index=3, no_enter=False):
    y, x = TUI.window.getmaxyx()
    message = message[:x - 2]
    TUI.window.addstr(int(y / 2),
                      int((TUI.width / 2) - len(message) / 2),
                      message,
                      curses.color_pair(color_pair_index))
    if not no_enter:
        string = "Press Enter to continue"[:x - 2]
        TUI.window.addstr(int(y / 2) + 1,
                          int((TUI.width / 2) - len(string) / 2),
                          string,
                          curses.color_pair(color_pair_index))

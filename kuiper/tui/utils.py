import curses
import re

from .states import RegisterState, LoginState
from ..models import User


def validate_email(email):
    return re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    email) and email.endswith("@utdallas.edu")


def validate_number(num):
    try:
        x = int(num)
        return x
    except ValueError as e:
        return False


def validate_user_registration(vals, sess):
    for key, value in zip(vals.keys(), vals.values()):
        if len(value) == 0 and key not in (RegisterState.REGISTER, RegisterState.BACK_TO_LOGIN):
            return "All fields are mandatory"
    if not validate_email(vals[RegisterState.EMAIL]):
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

    email_query = sess.query(User).filter(User.email == vals[RegisterState.EMAIL])
    if email_query.first():
        return "Email already taken"

    uname_query = sess.query(User).filter(User.username == vals[RegisterState.USERNAME])
    if uname_query.first():
        return "Username already taken"

    return "valid"


def validate_login(vals, sess):
    for key, value in zip(vals.keys(), vals.values()):
        if len(value) == 0 and key not in (LoginState.REGISTER, LoginState.LOGIN):
            return "All fields are mandatory"

    query = sess.query(User).filter((User.username == vals[LoginState.USERNAME] or
                                     User.email == vals[LoginState.USERNAME])
                                    and User.username == vals[LoginState.PASSWORD]).first()
    if not query:
        return "No account with that information was found"

    return query


def add_center_string(TUI, string, voffset, color_pair_index=1):
    _, x = TUI.window.getmaxyx()
    # Clip string so it doesn't go out of bounds
    string = string[:x - 2]
    TUI.window.addstr(voffset, int((TUI.width / 2) - len(string) / 2), string, curses.color_pair(color_pair_index))


def flash(TUI, message, color_pair_index=3):
    y, x = TUI.window.getmaxyx()
    for i, string in enumerate([message, "Press Enter to continue"]):
        string = string[:x - 2]
        TUI.window.addstr(int(y / 2) + i,
                          int((TUI.width / 2) - len(string) / 2),
                          string,
                          curses.color_pair(color_pair_index))

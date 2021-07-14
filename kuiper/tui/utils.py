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


class SuspendCurses:
    def __enter__(self):
        curses.endwin()

    def __exit__(self, exc_type, exc_val, exc_tb):
        newscr = curses.initscr()
        newscr.refresh()
        curses.doupdate()

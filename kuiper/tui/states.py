from enum import Enum


class WindowState(Enum):
    LOGIN = 1
    REGISTER = 2
    LOGOUT = 3

    FORUM_VIEW = 4
    POST_VIEW = 5
    NEW_POST_VIEW = 6

    ACCOUNT_DETAILS = 7
    HELP_MENU = 8


class LoginState(Enum):
    USERNAME = 1
    PASSWORD = 2

    LOGIN = 3
    REGISTER = 4

    EXIT = 5


class RegisterState(Enum):
    EMAIL = 0
    USERNAME = 1
    PASSWORD = 2

    AGE = 3
    MAJOR = 4

    REGISTER = 5
    BACK_TO_LOGIN = 6

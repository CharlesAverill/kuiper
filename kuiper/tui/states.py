from enum import Enum


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


class RegisterState(Enum):
    EMAIL = 0
    USERNAME = 1
    PASSWORD = 2

    AGE = 3
    MAJOR = 4

    REGISTER = 5
    BACK_TO_LOGIN = 6

from enum import Enum


class WindowState(Enum):
    LOGIN = 1
    REGISTER = 2
    LOGOUT = 3

    FORUM_VIEW = 4
    POST_VIEW = 5
    NEW_POST_VIEW = 6

    ACCOUNT_MENU = 7
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


class NewPostState(Enum):
    WAIT_FOR_VIM = 0
    REVIEW_POST = 1

    SUBMIT_POST = 2
    BACK_TO_VIM = 3

    SUBMITTED = 4


class AccountMenuState(Enum):
    USERNAME = 0
    AGE = 1
    MAJOR = 2
    
    RESET_PASSWORD = 3
    CONFIRM_PASSWORD = 4
    
    VIEW_MY_POST = 5
    DELETE_MY_POST = 6

    SUBMIT_UPDATES = 7
    BACK_TO_FORUM = 8


states_dicts = {
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
    },
    WindowState.ACCOUNT_MENU: {
        AccountMenuState.USERNAME: "username",
        AccountMenuState.AGE: "age",
        AccountMenuState.MAJOR: "major",
        AccountMenuState.RESET_PASSWORD: "reset_password",
        AccountMenuState.CONFIRM_PASSWORD: "confirm_password",
        AccountMenuState.SUBMIT_UPDATES: None,
        AccountMenuState.VIEW_MY_POST: None,
        AccountMenuState.DELETE_MY_POST: None,
        AccountMenuState.BACK_TO_FORUM: None
    }
}

states_lists = {
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
    ],
    WindowState.ACCOUNT_MENU: [
        AccountMenuState.USERNAME,
        AccountMenuState.AGE,
        AccountMenuState.MAJOR,
        AccountMenuState.RESET_PASSWORD,
        AccountMenuState.CONFIRM_PASSWORD,
        AccountMenuState.SUBMIT_UPDATES,
        AccountMenuState.VIEW_MY_POST,
        AccountMenuState.DELETE_MY_POST,
        AccountMenuState.BACK_TO_FORUM
    ]
}
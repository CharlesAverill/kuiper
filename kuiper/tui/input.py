import curses
import curses.ascii

from ..models import User

from .states import *
from .utils import validate_user_registration, validate_login


def shift_sub_states(TUI, ch, up=True, down=True):
    # Check for field changes, save to the buffers dictionary if changed, jump to next/prev field
    state_list = TUI.states_lists[TUI.state]
    if up and ch == curses.KEY_UP:
        TUI.buffers[TUI.sub_state] = TUI.current_buf
        TUI.sub_state = state_list[state_list.index(TUI.sub_state) - 1]
        TUI.current_buf = TUI.buffers[TUI.sub_state] if TUI.sub_state in TUI.buffers.keys() else ""
    elif down and ch == curses.KEY_DOWN:
        TUI.buffers[TUI.sub_state] = TUI.current_buf
        idx = state_list.index(TUI.sub_state) + 1
        TUI.sub_state = state_list[0 if idx > len(state_list) - 1 else idx]
        TUI.current_buf = TUI.buffers[TUI.sub_state] if TUI.sub_state in TUI.buffers.keys() else ""


def ilogin(TUI, ch):
    # Set validation values
    TUI.input_verification = curses.ascii.isalnum
    TUI.max_input_len = 20
    unctrl = curses.ascii.unctrl(ch)

    shift_sub_states(TUI, ch)

    # Carriage Return
    if ch == curses.KEY_ENTER or unctrl == "^I" or unctrl == "^J":
        if TUI.sub_state == LoginState.LOGIN:
            try:
                if validate_login(TUI.buffers):
                    TUI.flashing = "All fields are mandatory"
                elif TUI.client.login(TUI.buffers[LoginState.USERNAME], TUI.buffers[LoginState.PASSWORD]):
                    u = User()
                    u.from_json(TUI.client.get_user_by_username(TUI.buffers[LoginState.USERNAME]))
                    TUI.user = u
                    TUI.update_state(WindowState.FORUM_VIEW)
                else:
                    TUI.flashing = "No account found with that information"
            except ConnectionRefusedError:
                TUI.flashing = "Cannot find host, please check your internet connection"
        elif TUI.sub_state == LoginState.REGISTER:
            TUI.update_state(WindowState.REGISTER)
        elif TUI.sub_state == LoginState.EXIT:
            exit("Thank you for using kuiper!")
        else:
            shift_sub_states(TUI, curses.KEY_DOWN, up=False)


def iregister(TUI, ch):
    shift_sub_states(TUI, ch)
    unctrl = curses.ascii.unctrl(ch)

    if TUI.sub_state == RegisterState.AGE:
        TUI.max_input_len = 2
        TUI.input_verification = curses.ascii.isdigit
    elif TUI.sub_state == RegisterState.EMAIL:
        TUI.max_input_len = 40
        TUI.input_verification = curses.ascii.isprint
    else:
        TUI.max_input_len = 20
        TUI.input_verification = curses.ascii.isalnum

    # Carriage Return
    if ch == curses.KEY_ENTER or unctrl == "^I" or unctrl == "^J":
        if TUI.sub_state == RegisterState.REGISTER:
            # Perform Registration
            if TUI.reading_shorthand_input:
                TUI.shorthand_input()

            vals = TUI.buffers
            try:
                validation = validate_user_registration(vals, TUI.client, TUI.cfg)
                if validation == "valid":
                    # Submit registration to database
                    TUI.client.register(vals[RegisterState.EMAIL],
                                        vals[RegisterState.USERNAME],
                                        vals[RegisterState.PASSWORD],
                                        vals[RegisterState.AGE],
                                        vals[RegisterState.MAJOR])
                    # Go back to login page
                    TUI.update_state(WindowState.LOGIN)
                else:
                    TUI.flashing = validation
            except ConnectionRefusedError:
                TUI.flashing = "Cannot find host, please check your internet connection"
        elif TUI.sub_state == RegisterState.BACK_TO_LOGIN:
            TUI.update_state(WindowState.LOGIN)
        else:
            shift_sub_states(TUI, curses.KEY_DOWN, up=False)


def iforum(TUI, ch):
    unctrl = curses.ascii.unctrl(ch)
    if ch == curses.KEY_UP:
        TUI.scroll(TUI.UP)
    elif ch == curses.KEY_DOWN:
        TUI.scroll(TUI.DOWN)
    """
    elif ch == curses.KEY_LEFT:
        TUI.paging(TUI.UP)
    elif ch == curses.KEY_RIGHT:
        TUI.paging(TUI.DOWN)
    """
    if not TUI.reading_shorthand_input:
        if ch == curses.KEY_ENTER or unctrl == "^J":
            exit("Select")
        elif unctrl == "n":
            exit("New post")
        elif unctrl == "c":
            exit("Comment")
        elif unctrl == "h":
            exit("Help menu")
        elif unctrl == "a":
            exit("Account menu")
        elif unctrl == "p":
            exit("View post")
        elif unctrl == "l":
            TUI.user = None
            TUI.update_state(WindowState.LOGIN)


def inew_post(TUI, ch):
    unctrl = curses.ascii.unctrl(ch)
    if TUI.sub_state == NewPostState.REVIEW_POST:
        shift_sub_states(TUI, ch)
    if ch == curses.KEY_ENTER or unctrl == "^J":
        if TUI.sub_state == NewPostState.WAIT_FOR_VIM:
            exit("Open Vim")
    elif TUI.state == NewPostState.REVIEW_POST:
        if ch == curses.KEY_ENTER or unctrl == "^J":
            exit("Open Vim")

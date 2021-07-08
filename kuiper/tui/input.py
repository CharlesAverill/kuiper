import curses
import curses.ascii

from ..db import register

from .states import LoginState, WindowState, RegisterState
from .utils import validate_user_registration, validate_login, flash


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
    if ch == curses.KEY_ENTER or unctrl == "^J":
        if TUI.sub_state == LoginState.LOGIN:
            query_result = validate_login(TUI.buffers, TUI.sess)
            if type(query_result) != str:
                exit(query_result)
            else:
                TUI.flashing = query_result
        elif TUI.sub_state == LoginState.REGISTER:
            TUI.update_state(WindowState.REGISTER)
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
    if ch == curses.KEY_ENTER or unctrl == "^J":
        if TUI.sub_state == RegisterState.REGISTER:
            # Perform Registration
            if TUI.reading_shorthand_input:
                TUI.shorthand_input()

            vals = TUI.buffers
            validation = validate_user_registration(vals, TUI.sess)
            if validation == "valid":
                # Submit registration to database
                register(vals[RegisterState.EMAIL],
                         vals[RegisterState.USERNAME],
                         vals[RegisterState.PASSWORD],
                         vals[RegisterState.AGE],
                         vals[RegisterState.MAJOR],
                         TUI.sess)
                TUI.sess.commit()
                # Go back to login page
                TUI.update_state(WindowState.LOGIN)
            else:
                TUI.flashing = validation
        elif TUI.sub_state == RegisterState.BACK_TO_LOGIN:
            TUI.update_state(WindowState.LOGIN)
        else:
            shift_sub_states(TUI, curses.KEY_DOWN, up=False)


def iforum(TUI, ch):
    if ch == curses.KEY_UP:
        TUI.scroll(TUI.UP)
    elif ch == curses.KEY_DOWN:
        TUI.scroll(TUI.DOWN)
    elif ch == curses.KEY_LEFT:
        TUI.paging(TUI.UP)
    elif ch == curses.KEY_RIGHT:
        TUI.paging(TUI.DOWN)

import curses
import curses.ascii

from ..models import User

from .states import *
from .utils import validate_user_registration, validate_login


def ilogin(TUI, ch):
    # Set validation values
    TUI.shift_sub_states(ch)
    TUI.max_input_len = 20
    unctrl = curses.ascii.unctrl(ch)

    # Carriage Return
    if ch == curses.KEY_ENTER or unctrl == "^I" or unctrl == "^J":
        if TUI.sub_state == LoginState.LOGIN:
            if validate_login(TUI.buffers):
                TUI.flashing = "All fields are mandatory"
            elif TUI.client.login(TUI.buffers[LoginState.USERNAME], TUI.buffers[LoginState.PASSWORD]):
                u = User()
                u.from_json(TUI.client.get_user_by_username(TUI.buffers[LoginState.USERNAME]))
                TUI.user = u
                TUI.update_state(WindowState.FORUM_VIEW)
            else:
                TUI.flashing = "No account found with that information"
        elif TUI.sub_state == LoginState.REGISTER:
            TUI.update_state(WindowState.REGISTER)
        elif TUI.sub_state == LoginState.EXIT:
            exit("Thank you for using Kuiper!")
        else:
            TUI.shift_sub_states(curses.KEY_DOWN, up=False)


def iregister(TUI, ch):
    TUI.shift_sub_states(ch)

    unctrl = curses.ascii.unctrl(ch)

    # Carriage Return
    if ch == curses.KEY_ENTER or unctrl == "^I" or unctrl == "^J":
        if TUI.sub_state == RegisterState.REGISTER:
            vals = TUI.buffers
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
        elif TUI.sub_state == RegisterState.BACK_TO_LOGIN:
            TUI.update_state(WindowState.LOGIN)
        else:
            TUI.shift_sub_states(curses.KEY_DOWN, up=False)


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
            TUI.post_title = ""
            TUI.post_lines = []
            TUI.update_state(WindowState.NEW_POST_VIEW)
            TUI.sub_state = NewPostState.WAIT_FOR_VIM
        elif unctrl == "c":
            exit("Comment")
        elif unctrl == "h":
            TUI.update_state(WindowState.HELP_MENU)
        elif unctrl == "a":
            TUI.update_state(WindowState.ACCOUNT_MENU)
        elif unctrl == "r":
            TUI.reload_posts = True
            TUI.user_cache = {}
        elif unctrl == "l":
            TUI.user = None
            TUI.update_state(WindowState.LOGIN)


def inew_post(TUI, ch):
    unctrl = curses.ascii.unctrl(ch)

    if ch == curses.KEY_ENTER or unctrl == "^J":
        if TUI.sub_state == NewPostState.WAIT_FOR_VIM:
            # Get post from text editor
            if not TUI.get_from_text_editor():
                return
            TUI.sub_state = NewPostState.REVIEW_POST
            TUI.review_post_state = NewPostState.SUBMIT_POST
        elif TUI.sub_state == NewPostState.SUBMITTED:
            # Go back to forum
            TUI.post_lines = []
            TUI.post_title = ""
            TUI.update_state(WindowState.FORUM_VIEW)
    elif (ch == curses.KEY_BACKSPACE or unctrl == "^?") and TUI.sub_state == NewPostState.WAIT_FOR_VIM:
        # Go back to forum
        TUI.post_lines = []
        TUI.post_title = ""
        TUI.update_state(WindowState.FORUM_VIEW)
    elif unctrl == "s" and TUI.sub_state == NewPostState.REVIEW_POST:
        # Submit post to database
        if TUI.client.create_post(TUI.post_title, "\n".join(TUI.post_lines).strip(), TUI.user.id):
            TUI.sub_state = NewPostState.SUBMITTED
        else:
            TUI.flashing = "There was an error submitting your post"
    elif unctrl == "m" and TUI.sub_state == NewPostState.REVIEW_POST:
        TUI.sub_state = NewPostState.WAIT_FOR_VIM
        TUI.review_post_state = NewPostState.SUBMIT_POST


def iaccount_menu(TUI, ch):
    # Set validation values
    TUI.shift_sub_states(ch)
    TUI.max_input_len = 20
    unctrl = curses.ascii.unctrl(ch)

    # Carriage Return
    if ch == curses.KEY_ENTER or unctrl == "^I" or unctrl == "^J":
        if TUI.sub_state == AccountMenuState.VIEW_MY_POST:
            exit("View My Post")
        elif TUI.sub_state == AccountMenuState.DELETE_MY_POST:
            if TUI.client.delete_post(TUI.user.post_id):
                TUI.flashing = "Post Deleted"
            else:
                TUI.flashing = "Unable to delete your post. Are you sure you've made one?"
        elif TUI.sub_state == AccountMenuState.SUBMIT_UPDATES:
            rp = TUI.buffers[AccountMenuState.RESET_PASSWORD] if AccountMenuState.RESET_PASSWORD in TUI.buffers \
                else None
            cp = TUI.buffers[AccountMenuState.CONFIRM_PASSWORD] if AccountMenuState.CONFIRM_PASSWORD in TUI.buffers \
                else None
            if (rp or cp) and rp != cp:
                TUI.flashing = "Passwords do not match"
            else:
                payload = {}
                for key in TUI.buffers.keys():
                    if not TUI.buffers[key]:
                        continue
                    if key == AccountMenuState.USERNAME:
                        payload["USERNAME"] = TUI.buffers[key]
                    if key == AccountMenuState.AGE:
                        payload["AGE"] = TUI.buffers[key]
                    if key == AccountMenuState.MAJOR:
                        payload["MAJOR"] = TUI.buffers[key]
                    if key == AccountMenuState.CONFIRM_PASSWORD:
                        payload["PASSWORD"] = TUI.buffers[key]
                if TUI.client.update_user(TUI.user.id, payload):
                    TUI.flashing = "Account updated"
                else:
                    TUI.flashing = "Account could not be updated"
        elif TUI.sub_state == AccountMenuState.BACK_TO_FORUM:
            TUI.update_state(WindowState.FORUM_VIEW)
        else:
            TUI.shift_sub_states(curses.KEY_DOWN, up=False)


def ihelp(TUI, ch):
    str(ch)
    TUI.update_state(WindowState.FORUM_VIEW)

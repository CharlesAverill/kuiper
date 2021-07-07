from curses import wrapper

sess = None


def main(stdscr):
    global sess
    stdscr.clear()

    stdscr.box()

    # This raises ZeroDivisionError when i == 10.
    for i in range(0, 9):
        v = i - 10
        stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10 / v))

    stdscr.refresh()
    stdscr.getkey()


def start_tui(session):
    global sess
    sess = session

    wrapper(main)

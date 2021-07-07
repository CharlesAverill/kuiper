from .init_db import init_db
from .db import register, create_post
from .tui import start_tui


def main():
    sess = init_db()

    start_tui(sess)


if __name__ == "__main__":
    main()

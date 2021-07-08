from .init_db import init_db
from .tui import start_tui
from .models import User


def main():
    sess = init_db()

    start_tui(sess)


if __name__ == "__main__":
    main()

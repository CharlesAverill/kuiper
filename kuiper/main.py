import argparse

from .init_db import init_db
from .tui import start_tui

ascii_art = r"""
┌───────────────────────────────────────────────────────────────┐
│     __                  __                                    │
│    |  \                |  \                                   │
│    | $$   __  __    __  \$$  ______    ______    ______       │
│    | $$  /  \|  \  |  \|  \ /      \  /      \  /      \      │
│    | $$_/  $$| $$  | $$| $$|  $$$$$$\|  $$$$$$\|  $$$$$$\     │
│    | $$   $$ | $$  | $$| $$| $$  | $$| $$    $$| $$   \$$     │
│    | $$$$$$\ | $$__/ $$| $$| $$__/ $$| $$$$$$$$| $$           │
│    | $$  \$$\ \$$    $$| $$| $$    $$ \$$     \| $$           │
│     \$$   \$$  \$$$$$$  \$$| $$$$$$$   \$$$$$$$ \$$           │
│                            | $$                               │
│                            | $$                               │
│                             \$$                               │
│                        Charles Averill                        │
│charles.averill@utdallas.edu  https://github.com/CharlesAverill│
└───────────────────────────────────────────────────────────────┘
"""


def main():
    parser = argparse.ArgumentParser(description=ascii_art, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-c",
                        "--credentials",
                        help="Your username/email and password, separated by a space and wrapped with quotes",
                        default=None,
                        type=str)

    args = parser.parse_args()

    if args.credentials:
        exit(args.credentials)

    sess = init_db()

    start_tui(sess)


if __name__ == "__main__":
    main()

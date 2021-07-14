import argparse
import os
import pathlib
import time
import update_checker

from yaml import load, dump, FullLoader, SafeDumper

from .db import init_db
from .tui import start_tui
from .remote import Client, start_server
from . import __version__

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
                        default=None)
    parser.add_argument("-d",
                        "--dump_configs",
                        help="Prints out your configs",
                        action="store_true")
    parser.add_argument("-i",
                        "--init_db",
                        action="store_true",
                        help="Initializes database(s) required for operation")
    parser.add_argument("-l",
                        "--load_configs",
                        help="Path to a .yaml file for server configurations")
    parser.add_argument("--local_server",
                        action="store_true",
                        help="Access a server on 127.0.0.1 instead of the access_host in your configurations")
    parser.add_argument("-q",
                        "--quiet",
                        action="store_true",
                        help="Suppresses server output")
    parser.add_argument("-s",
                        "--server",
                        action="store_true",
                        help="Starts up a Kuiper server")

    args = parser.parse_args()

    cfg_path = pathlib.Path(os.path.dirname(__file__)).parents[0] / "config.yaml"

    with open(cfg_path, "r") as cfg_stream:
        cfg = load(cfg_stream, FullLoader)

    if args.credentials:
        exit(args.credentials)

    if args.init_db:
        init_db(cfg, delete_db=True)
        exit("Database initialized")

    if args.load_configs:
        with open(args.load_configs, "r") as new_stream:
            cfg.update(load(new_stream, FullLoader))
            with open(cfg_path, "w") as old_stream:
                dump(cfg, old_stream, SafeDumper)
        exit("Configurations loaded")

    if args.dump_configs:
        for key, val in cfg.items():
            print(f"{key}: {val}")
        exit()

    if args.local_server:
        cfg["access_host"] = "127.0.0.1"

    uc = update_checker.UpdateChecker()
    result = uc.check("kuiper", __version__)
    if result:
        print(result)
        time.sleep(2)

    if args.server:
        sess = init_db(cfg, delete_db=False)
        start_server(cfg, sess, args.quiet)
    else:
        client = Client(cfg["access_host"], cfg["port"])
        start_tui(client, cfg)


if __name__ == "__main__":
    main()

from init_db import init_db
from db import register, create_post
from tui import start_tui

sess = init_db()

start_tui(sess)

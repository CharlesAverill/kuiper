from yaml import load, FullLoader

from .models import User, Post, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import pathlib


def init_db():
    path = pathlib.Path(os.path.dirname(__file__)).parents[0] / "config.yaml"

    with open(path, "r") as cfg_stream:
        cfg = load(cfg_stream, FullLoader)

    engine = create_engine("sqlite:///" + cfg["db_path"])
    Base.metadata.create_all(engine)

    sess = sessionmaker(engine)

    return sess()


def register(email, username, password, age, major, session):
    u = User()

    u.email = email
    u.username = username
    u.password = password
    u.age = age
    u.major = major

    session.add(u)


def create_post(content, user, session):
    p = Post()
    p.content = content

    if len(user.post) > 0:
        user.post[0].user = None
        user.post.append(p)

    session.add(p)

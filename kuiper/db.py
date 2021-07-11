from .models import User, Post, Base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

import datetime
import os


def init_db(cfg, delete_db=False):
    if delete_db:
        os.unlink(cfg["db_path"])

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
    session.commit()


def create_post(title, content, user, session):
    p = Post()
    p.title = title
    p.content = content
    p.created_at = datetime.datetime.now()

    if len(user.post) > 0:
        user.post[0].user = None
        user.post.append(p)

    session.add(p)
    session.commit()


def login(username, password, session):
    query = session.query(User).filter(User.username == username, User.password == password).first()

    if not query:
        return None

    return query.json()


def get_user_by_username(username, session):
    query = session.query(User).filter(User.username == username).first()

    if not query:
        return None

    return query.json()


def get_user_by_email(email, session):
    query = session.query(User).filter(User.email == email).first()

    if not query:
        return None

    return query.json()


def get_post(post_id, session):
    query = session.query(Post).filter(Post.id == post_id).first()

    if not query:
        return None

    return query.json()

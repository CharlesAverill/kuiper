from .models import User, Post, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

import datetime
import os
import uuid


logged_in = {}


def is_logged_in(user_id):
    global logged_in

    remove = []
    found = False

    for k, v in logged_in.items():
        if (datetime.datetime.now() - v).seconds / 60 > 15:  # 15 minute timeout
            remove.append(k)
        elif k == user_id:
            logged_in[k] = datetime.datetime.now()
            found = True

    for k in remove:
        del logged_in[k]

    return found


def init_db(cfg, delete_db=False):
    if delete_db:
        os.unlink(cfg["db_path"])

    engine = create_engine("sqlite:///" + cfg["db_path"])
    if delete_db:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    sess = sessionmaker(engine)

    return sess()


def register(email, username, password, age, major, session):
    u = User()

    u.id = str(uuid.uuid4())
    u.email = email
    u.username = username
    u.password = generate_password_hash(password)
    u.age = age
    u.major = major

    session.add(u)
    session.commit()


def create_post(title, content, user_id, username, session):
    p = Post()
    p.title = title
    p.content = content
    p.created_at = datetime.datetime.now()
    p.user_username = username

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    if user.post_id:
        session.query(Post).filter(Post.user_username == username).delete()

    session.add(p)
    session.commit()

    user.post_id = p.id

    session.commit()


def login(username, password, session):
    global logged_in

    query = session.query(User).filter(User.username == username).first()

    if not query or not check_password_hash(query.password, password):
        return None

    logged_in.update({query.id: datetime.datetime.now()})

    return query.json()


def get_user_by_username(username, session):
    query = session.query(User).filter(User.username == username).first()

    if not query:
        return None

    query.id = None

    return query.json()


def get_user_by_email(email, session):
    query = session.query(User).filter(User.email == email).first()

    if not query:
        return None

    return query.json()


def get_user_by_id(user_id, session):
    query = session.query(User).filter(User.id == user_id).first()

    if not query:
        return None

    return query.json()


def get_post(post_id, session):
    query = session.query(Post).filter(Post.id == post_id).first()

    if not query:
        return None

    return query.json()


def get_all_posts(session):
    query = session.query(Post).all()

    # Space is important
    out = "[ "

    for p in query:
        out += p.json() + ","

    # Remove last comma
    return out[:-1] + "]"


def update_user(user_id, new_values, session):
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        return False

    for key in new_values.keys():
        if key == "USERNAME":
            user.username = new_values[key]
        elif key == "AGE":
            user.age = new_values[key]
        elif key == "MAJOR":
            user.major = new_values[key]
        elif key == "PASSWORD":
            user.password = generate_password_hash(new_values[key])

    return True


def delete_post(post_id, session):
    query = session.query(Post).filter(Post.id == post_id)
    if query.first():
        query.delete()
        return True
    else:
        return False

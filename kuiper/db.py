from .models import User, Post


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

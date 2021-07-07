from .models import User, Post


def register(name, age, major, session):
    u = User()

    u.name = name
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

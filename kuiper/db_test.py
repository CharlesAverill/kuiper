from .models import User, Post
from .init_db import init_db

sess = init_db()

u = User()
u.name = "Charles Averill"
u.age = 18
u.major = "CS"

p = Post()
p.content = "Hello world!\n" \
            "This is the second line!"

u.post.append(p)
print(p.user)

sess.add(u)
sess.add(p)

sess.commit()

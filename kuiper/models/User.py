from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime, Text

from . import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(Text)
    username = Column(Text(length=20))
    password = Column(Text(length=20))

    age = Column(Integer)
    major = Column(Text(length=20))

    post = relationship("Post", back_populates="user")
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    __tablename__ = "user"

    def __str__(self):
        out = f"ID: {self.id}\n" \
              f"Username: {self.username}\n" \
              f"Email: {self.email}\n" \
              f"Age: {self.age}"

        if self.major:
            out += f"\nMajor: {self.major}"
        if self.post:
            out += f"\nPost ID: {self.post[0].id}"

        return out

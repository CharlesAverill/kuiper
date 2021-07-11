import json

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

    def from_json(self, data):
        self.id = data["USER_ID"]
        self.email = data["EMAIL"]
        self.username = data["USERNAME"]
        self.age = int(data["AGE"])
        self.major = data["MAJOR"]

    def json(self):
        data = {
            "USER_ID": self.id,
            "EMAIL": self.email,
            "USERNAME": self.username,
            "AGE": self.age,
            "MAJOR": self.major,
        }
        if len(self.post) > 0:
            data["POST_ID"] = self.post[0].id

        return json.dumps(data)

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

import datetime
import json

from sqlalchemy.sql.functions import now
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime, Text

from . import Base


class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(Text)
    username = Column(Text(length=20))
    password = Column(Text)

    age = Column(Integer)
    major = Column(Text(length=20))

    post_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    __tablename__ = "user"

    def __init__(self):
        self.created_at = datetime.datetime.now()

    def from_json(self, data):
        self.id = data["USER_ID"]
        self.email = data["EMAIL"]
        self.username = data["USERNAME"]
        self.age = int(data["AGE"])
        self.major = data["MAJOR"]
        if "POST_ID" in data.keys():
            self.post_id = data["POST_ID"]

    def json(self):
        data = {
            "USER_ID": self.id,
            "EMAIL": self.email,
            "USERNAME": self.username,
            "AGE": self.age,
            "MAJOR": self.major,
        }
        if self.post_id:
            data["POST_ID"] = self.post_id

        return json.dumps(data)

    def __str__(self):
        out = f"ID: {self.id}\n" \
              f"Username: {self.username}\n" \
              f"Email: {self.email}\n" \
              f"Age: {self.age}\n" \
              f"Post ID: {self.post_id}"

        if self.major:
            out += f"\nMajor: {self.major}"
        if self.post_id:
            out += f"\nPost ID: {self.post_id}"

        return out

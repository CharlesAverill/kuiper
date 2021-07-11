import datetime
import json

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime, Integer, UnicodeText

from . import Base


date_format = "%m-%d %H%M%S"


class Post(Base):
    id = Column(Integer, primary_key=True)

    title = Column(UnicodeText, nullable=False)
    content = Column(UnicodeText, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="post")

    __tablename__ = "post"

    def __init__(self):
        self.created_at = datetime.datetime.now()

    @property
    def time_left(self):
        td = datetime.datetime.now() - self.created_at
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"

    def from_json(self, data):
        self.id = data["POST_ID"]
        self.title = data["TITLE"]
        self.content = data["CONTENT"]
        self.created_at = datetime.datetime.strptime(data["CREATED_AT"], date_format)

    def json(self):
        return json.dumps({
            "POST_ID": self.id,
            "TITLE": self.title,
            "CONTENT": self.content,
            "CREATED_AT": self.created_at.strftime(date_format),
            "USER_ID": self.user_id
        })

    def __str__(self):
        return f"{self.user.username}\n" \
               f"{self.title}\n" \
               f"{self.time_left[:2]}H"

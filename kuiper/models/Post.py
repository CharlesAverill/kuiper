import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime, Integer, UnicodeText

from . import Base


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

    def __str__(self):
        return f"{self.user.username}\n" \
               f"{self.title}\n" \
               f"{self.time_left[:2]}H"

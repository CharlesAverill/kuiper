from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime, Integer, UnicodeText, Unicode

from . import Base
from .User import User


class Post(Base):
    id = Column(Integer, primary_key=True)

    content = Column(UnicodeText, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="post")

    __tablename__ = "post"

    def __str__(self):
        return f"ID: {self.id}\n" \
               f"User ID: {self.user_id}\n" \
               f"---Content---\n{self.content}\n-------------"

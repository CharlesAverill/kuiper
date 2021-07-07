from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime, Text

from . import Base


class User(Base):
    id = Column(Integer, primary_key=True)

    name = Column(Text(length=40), nullable=False)
    age = Column(Integer, nullable=False)
    major = Column(Text(length=40))

    post = relationship("Post", back_populates="user")
    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    __tablename__ = "user"

    def __str__(self):
        out = f"ID: {self.id}\n" \
              f"Name: {self.name}\n" \
              f"Age: {self.age}"

        if self.major:
            out += f"\nMajor: {self.major}"
        if self.post:
            out += f"\nPost ID: {self.post[0].id}"

        return out

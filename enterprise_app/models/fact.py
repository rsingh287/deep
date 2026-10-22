from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from ..core.database import Base


class Fact(Base):
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    concept = Column(String, index=True, nullable=False)
    facts = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

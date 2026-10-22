from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from enterprise_app.core.database import Base


class AgentSkill(Base):
    __tablename__ = "agent_skills"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    plugin = Column(String, nullable=True)
    scope = Column(String, nullable=True, default="Global")
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

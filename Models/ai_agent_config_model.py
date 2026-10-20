from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime
from datetime import datetime

class AIAgentConfigModel(BASE):

    __tablename__ = "ai_agent_config"

    id = Column(BigInteger, primary_key=True)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

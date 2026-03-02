from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class ServiceStatusModel(BASE):

    __tablename__ = "service_status"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

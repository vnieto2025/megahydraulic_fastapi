from Config.db import BASE
from sqlalchemy import BigInteger, Column, String, Integer, DECIMAL, DateTime
from datetime import datetime


class ServiceActivitiesModel(BASE):

    __tablename__ = "service_activities"

    id          = Column(BigInteger, primary_key=True, autoincrement=True)
    sap_code    = Column(String(20))
    description = Column(String(255), nullable=False)
    unit_price  = Column(DECIMAL(15, 2), default=0)
    status      = Column(Integer, default=1)
    created_at  = Column(DateTime, default=datetime.now)

    def __init__(self, data: dict):
        self.sap_code    = data.get("sap_code")
        self.description = data.get("description")
        self.unit_price  = data.get("unit_price", 0)
        self.status      = data.get("status", 1)

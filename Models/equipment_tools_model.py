from Config.db import BASE
from sqlalchemy import BigInteger, Column, String, Integer, DECIMAL, DateTime
from datetime import datetime


class EquipmentToolsModel(BASE):

    __tablename__ = "equipment_tools"

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    name       = Column(String(150), nullable=False)
    unit       = Column(String(20), default='HRS')
    unit_price = Column(DECIMAL(15, 2), default=0)
    status     = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)

    def __init__(self, data: dict):
        self.name       = data.get("name")
        self.unit       = data.get("unit", "HRS")
        self.unit_price = data.get("unit_price", 0)
        self.status     = data.get("status", 1)

from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, DECIMAL
from datetime import datetime


class LaborTypeModel(BASE):
    __tablename__ = "labor_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    unit = Column(String(20), nullable=False, default='HH')
    value = Column(DECIMAL(15, 2), nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.code = data['code']
        self.description = data['description']
        self.unit = data.get('unit', 'HH')
        self.value = data.get('value', 0)

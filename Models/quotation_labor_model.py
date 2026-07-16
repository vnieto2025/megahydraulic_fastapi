from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime, DECIMAL, UnicodeText
from datetime import datetime


class QuotationLaborModel(BASE):
    __tablename__ = "quotation_labor"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quotation_id = Column(BigInteger, nullable=False)
    labor_type_id = Column(BigInteger, nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False, default=0)
    unit_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    total_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    description = Column(UnicodeText, nullable=True)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.quotation_id = data['quotation_id']
        self.labor_type_id = data['labor_type_id']
        self.quantity = data.get('quantity', 0)
        self.unit_price = data.get('unit_price', 0)
        self.total_price = data.get('total_price', 0)
        self.description = data.get('description')

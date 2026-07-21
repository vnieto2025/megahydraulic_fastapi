from Config.db import BASE
from sqlalchemy import Column, BigInteger, Text, Integer, DateTime
from datetime import datetime

class QuotationPhotosModel(BASE):

    __tablename__ = "quotation_photos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quotation_id = Column(BigInteger, nullable=False)
    path = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.quotation_id = data['quotation_id']
        self.path = data['path']
        self.description = data.get('description')

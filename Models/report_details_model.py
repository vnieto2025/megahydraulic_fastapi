from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Text
from datetime import datetime

class ReportDetailsModel(BASE):

    __tablename__= "report_details"
    
    id = Column(BigInteger, primary_key=True)
    report_id = Column(BigInteger, nullable=False)
    task_id = Column(BigInteger, nullable=False)
    positive = Column(Integer, nullable=True, default=0)
    negative = Column(Integer, nullable=True, default=0)
    description = Column(Text)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.report_id = data['report_id']
        self.task_id = data['task_id']
        self.positive = data['positive']
        self.negative = data['negative']
        self.description = data['description']

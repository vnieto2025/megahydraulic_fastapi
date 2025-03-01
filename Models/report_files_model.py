from Config.db import BASE
from sqlalchemy import Column, BigInteger, Text, Integer, DateTime
from datetime import datetime

class ReportFilesModel(BASE):

    __tablename__= "report_files"
    
    id = Column(BigInteger, primary_key=True)
    report_id = Column(BigInteger, nullable=False)
    path = Column(Text)
    description = Column(Text)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.report_id = data['report_id']
        self.path = data['path']
        self.description = data['description']

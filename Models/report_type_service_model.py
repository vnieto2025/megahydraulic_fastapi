from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class ReportTypeServiceModel(BASE):

    __tablename__= "report_type_service"
    
    id = Column(BigInteger, primary_key=True)
    report_id = Column(BigInteger, nullable=False)
    type_service_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.report_id = data['report_id']
        self.type_service_id = data['type_service_id']
 
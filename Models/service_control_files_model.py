from Config.db import BASE
from sqlalchemy import Column, BigInteger, Text, Integer, DateTime
from datetime import datetime

class ServiceControlFilesModel(BASE):

    __tablename__ = "service_control_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    service_control_id = Column(BigInteger, nullable=False)
    path = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.service_control_id = data['service_control_id']
        self.path = data['path']
        self.description = data.get('description')

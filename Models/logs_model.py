from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, DateTime, Text
from datetime import datetime

class LogsModel(BASE):

    __tablename__= "logs"
    
    id = Column(BigInteger, primary_key=True)
    service = Column(String, nullable=False)
    method = Column(String, nullable=False)
    request = Column(Text)
    response = Column(Text)
    ip = Column(String, nullable=True)
    created_at = Column(DateTime(), default=datetime.now, nullable=False)

    def __init__(self, data: dict):
        self.service = data['service']
        self.method = data['method']
        self.request = data['request']
        self.response = data['response']
        self.ip = data['ip']
        if 'created_at' in data:
            self.created_at = data['created_at']

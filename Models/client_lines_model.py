from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class ClientLinesModel(BASE):

    __tablename__= "client_lines"
    
    id = Column(BigInteger, primary_key=True)
    client_id = Column(BigInteger, nullable=False)
    name = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.client_id = data['client_id']
        self.name = data['name']

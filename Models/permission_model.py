from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime, Text
from datetime import datetime

class PermissionModel(BASE):

    __tablename__= "permission"
    
    id = Column(BigInteger, primary_key=True)
    type_user_id = Column(BigInteger, nullable=False)
    module_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.type_user_id = data['type_user_id']
        self.module_id = data['module_id']

from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime

class TypeEquipmentModel(BASE):

    __tablename__= "type_equipment_intervened"
    
    id = Column(BigInteger, primary_key=True)
    order = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

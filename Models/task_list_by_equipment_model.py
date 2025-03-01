from Config.db import BASE
from sqlalchemy import Column, BigInteger, Integer, DateTime
from datetime import datetime

class TaskListEquipmentModel(BASE):

    __tablename__= "task_list_by_equipment"
    
    id = Column(BigInteger, primary_key=True)
    equipment_id = Column(BigInteger, nullable=False)
    task_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
 
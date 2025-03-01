from Config.db import BASE
from sqlalchemy import Column, BigInteger

class ReportTypeMaintenanceModel(BASE):

    __tablename__= "report_type_maintenance"
    
    id = Column(BigInteger, primary_key=True)
    id_report = Column(BigInteger, nullable=False)
    type_maintenance_id = Column(BigInteger, nullable=False)

    def __init__(self, data: dict):
        self.id_report = data['id_report']
        self.type_maintenance_id = data['type_maintenance_id']

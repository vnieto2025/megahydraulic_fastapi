from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Text
from datetime import datetime

class ReportModel(BASE):

    __tablename__= "reports"
    
    id = Column(BigInteger, primary_key=True)
    activity_date = Column(DateTime, nullable=False)
    client_id = Column(BigInteger, nullable=False)
    client_line_id = Column(BigInteger, nullable=False)
    person_receives = Column(String, nullable=False)
    om = Column(String, nullable=True)
    solped = Column(String, nullable=True)
    buy_order = Column(String, nullable=True)
    position = Column(String, nullable=True)
    equipment_type_id = Column(BigInteger, nullable=False)
    equipment_name = Column(String, nullable=False)
    service_description = Column(Text)
    information = Column(Text)
    user_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.activity_date = data['activity_date']
        self.client_id = data['client_id']
        self.client_line_id = data['client_line_id']
        self.person_receives = data['person_receives']
        self.om = data['om']
        self.solped = data['solped']
        self.buy_order = data['buy_order']
        self.position = data['position']
        self.equipment_type_id = data['equipment_type_id']
        self.equipment_name = data['equipment_name']
        self.service_description = data['service_description']
        self.information = data['information']
        self.user_id = data['user_id']

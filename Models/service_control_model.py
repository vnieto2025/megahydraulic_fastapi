from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Text, DECIMAL, Date
from datetime import datetime

class ServiceControlModel(BASE):

    __tablename__ = "service_control"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    activity_date = Column(Date, nullable=False)
    client_id = Column(BigInteger, nullable=False)
    client_line_id = Column(BigInteger, nullable=False)
    responsible_id = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=True)
    information = Column(Text, nullable=True)
    service_order = Column(String(100), nullable=True)
    quotation = Column(String(100), nullable=True)
    # component: 0=Hidráulico, 1=Suministro, 2=Mecánico
    component = Column(Integer, nullable=True)
    component_quantity = Column(Integer, nullable=True, default=0)
    value = Column(DECIMAL(15, 2), nullable=True, default=0)
    solped = Column(String(100), nullable=True)
    oc = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    # status: 0=Por aprobar, 1=En ejecución, 2=Por facturar, 3=Facturado
    service_status = Column(Integer, nullable=False, default=0)
    # report_status: 0=Por hacer, 1=Por enviar, 2=Enviado
    report_status = Column(Integer, nullable=False, default=0)
    consecutive = Column(BigInteger, nullable=True)
    invoice = Column(Integer, nullable=True)
    invoice_date = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    report_id = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.activity_date = data['activity_date']
        self.client_id = data['client_id']
        self.client_line_id = data['client_line_id']
        self.responsible_id = data['responsible_id']
        self.description = data['description']
        self.information = data['information']
        self.service_order = data['service_order']
        self.quotation = data['quotation']
        self.component = data['component']
        self.component_quantity = data['component_quantity']
        self.value = data['value']
        self.solped = data['solped']
        self.oc = data['oc']
        self.position = data['position']
        self.service_status = data['service_status']
        self.report_status = data['report_status']
        self.consecutive = data['consecutive']
        self.invoice = data['invoice']
        self.invoice_date = data['invoice_date']
        self.note = data['note']
        self.report_id = data.get('report_id', None)
        self.user_id = data['user_id']

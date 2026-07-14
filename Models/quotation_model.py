from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Text, DECIMAL, Date
from datetime import datetime


class QuotationModel(BASE):
    """
    Cabecera de cotización.
    quotation_number se genera como: {prefix}-{consecutive:05d}  → ej. MP1-00500
    """
    __tablename__ = "quotations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    plant_id = Column(BigInteger, nullable=False)           # FK → quotation_plants.id
    quotation_number = Column(String(20), nullable=False)   # "MP1-00500"
    city = Column(String(100), nullable=True)
    activity_date = Column(Date, nullable=False)
    client_id = Column(BigInteger, nullable=False)
    client_line_id = Column(BigInteger, nullable=True)
    responsible_id = Column(BigInteger, nullable=True)
    phone = Column(String(30), nullable=True)
    nit = Column(String(30), nullable=True)
    scope = Column(Text, nullable=True)                     # alcance de la actividad
    delivery_time = Column(String(200), nullable=True)      # tiempo de entrega
    activity_description = Column(Text, nullable=True)      # descripción de la actividad
    execution_place = Column(String(200), nullable=True)    # donde se ejecuta
    subtotal = Column(DECIMAL(15, 2), nullable=False, default=0)
    subtotal_with_iva = Column(DECIMAL(15, 2), nullable=False, default=0)
    user_id = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)
    updated_at = Column(DateTime(), default=datetime.now(), onupdate=datetime.now, nullable=False)

    def __init__(self, data: dict):
        self.plant_id = data['plant_id']
        self.quotation_number = data['quotation_number']
        self.city = data.get('city')
        self.activity_date = data['activity_date']
        self.client_id = data['client_id']
        self.client_line_id = data.get('client_line_id')
        self.responsible_id = data.get('responsible_id')
        self.phone = data.get('phone')
        self.nit = data.get('nit')
        self.scope = data.get('scope')
        self.delivery_time = data.get('delivery_time')
        self.activity_description = data.get('activity_description')
        self.execution_place = data.get('execution_place')
        self.subtotal = data.get('subtotal', 0)
        self.subtotal_with_iva = data.get('subtotal_with_iva', 0)
        self.user_id = data['user_id']

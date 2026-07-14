from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, Text, DECIMAL, DateTime
from datetime import datetime


class QuotationItemModel(BASE):
    """
    Ítems de una cotización.
    item_type distingue filas:
      'item'      → ítem normal del cuadro de cantidades
      'logistics' → fila fija "Logística y Transporte"
      'surcharge' → fila fija "Trabajo en Altura / Recargos"
    """
    __tablename__ = "quotation_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quotation_id = Column(BigInteger, nullable=False)       # FK → quotations.id
    item_order = Column(Integer, nullable=True)             # posición dentro del cuadro (null en filas fijas)
    sap_code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String(20), nullable=True)
    quantity = Column(DECIMAL(10, 2), nullable=False, default=0)
    unit_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    total_price = Column(DECIMAL(15, 2), nullable=False, default=0)  # quantity × unit_price
    item_type = Column(String(20), nullable=False, default='item')   # 'item' | 'logistics' | 'surcharge'
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.quotation_id = data['quotation_id']
        self.item_order = data.get('item_order')
        self.sap_code = data.get('sap_code')
        self.description = data.get('description')
        self.unit = data.get('unit')
        self.quantity = data.get('quantity', 0)
        self.unit_price = data.get('unit_price', 0)
        self.total_price = data.get('total_price', 0)
        self.item_type = data.get('item_type', 'item')

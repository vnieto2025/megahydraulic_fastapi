from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, Text, DECIMAL, DateTime, UnicodeText
from datetime import datetime


class QuotationItemModel(BASE):
    """
    Ítems de una cotización.
    item_type:
      'item'             → cuadro de cantidades de obra
      'logistics'        → logística y transporte (fila fija)
      'surcharge'        → trabajo en altura (fila fija)
      'material'         → análisis APU materiales
      'equipment'        → análisis APU equipos y herramientas
      'hourly_surcharge' → análisis APU recargo horas adicional
    """
    __tablename__ = "quotation_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    quotation_id = Column(BigInteger, nullable=False)
    item_order = Column(Integer, nullable=True)
    sap_code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String(20), nullable=True)
    quantity = Column(DECIMAL(10, 2), nullable=False, default=0)
    unit_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    total_price = Column(DECIMAL(15, 2), nullable=False, default=0)
    surcharge_percent = Column(DECIMAL(7, 2), nullable=True)   # solo para hourly_surcharge: qty*price*(pct/100)
    row_description = Column(UnicodeText, nullable=True)        # desarrollo de la actividad
    item_type = Column(String(30), nullable=False, default='item')
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
        self.surcharge_percent = data.get('surcharge_percent')
        self.row_description = data.get('row_description')
        self.item_type = data.get('item_type', 'item')

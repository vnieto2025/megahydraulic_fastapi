from Config.db import BASE
from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from datetime import datetime


class QuotationPlantModel(BASE):
    """
    Plantas de cotización. Cada planta tiene su propio prefijo y consecutivo.
    Ejemplo: Planta 1 → prefijo 'MP1', consecutivo empieza en 500 → MP1-00500
    """
    __tablename__ = "quotation_plants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)          # "Planta 1", "Planta 2"
    prefix = Column(String(10), nullable=False)         # "MP1", "MP2"
    consecutive = Column(Integer, nullable=False, default=500)  # próximo número a usar
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(), default=datetime.now(), nullable=False)

    def __init__(self, data: dict):
        self.name = data['name']
        self.prefix = data['prefix']
        self.consecutive = data.get('consecutive', 500)

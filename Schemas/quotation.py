from pydantic import BaseModel
from typing import Optional, List


class QuotationItem(BaseModel):
    sap_code: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    quantity: float = 0
    unit_price: float = 0
    total_price: float = 0
    item_type: str = 'item'   # 'item' | 'logistics' | 'surcharge'


class Quotation(BaseModel):
    plant_id: int
    city: Optional[str] = None
    activity_date: str
    client_id: int
    client_line_id: Optional[int] = None
    responsible_id: Optional[int] = None
    phone: Optional[str] = None
    nit: Optional[str] = None
    scope: Optional[str] = None
    delivery_time: Optional[str] = None
    activity_description: Optional[str] = None
    execution_place: Optional[str] = None
    subtotal: float = 0
    user_id: int
    items: List[QuotationItem] = []

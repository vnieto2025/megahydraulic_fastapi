from pydantic import BaseModel
from typing import Optional

class ServiceControl(BaseModel):
    activity_date: str
    client_id: int
    client_line_id: int
    responsible_id: int
    description: Optional[str] = None
    service_order: Optional[str] = None
    quotation: Optional[str] = None
    component: int
    component_quantity: Optional[int] = None
    value: Optional[float] = None
    solped: Optional[str] = None
    oc: Optional[str] = None
    position: Optional[str] = None
    service_status: int
    report_status: int
    consecutive: Optional[int] = None
    invoice: Optional[int] = None
    invoice_date: Optional[str] = None
    note: Optional[str] = None
    report_id: Optional[int] = None
    user_id: int

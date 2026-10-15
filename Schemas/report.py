from pydantic import BaseModel
from typing import Optional

class Report(BaseModel):
    activity_date: str
    client_id: int
    client_line_id: int
    person_receives: int
    om: Optional[str] = None
    equipment_type_id: int
    equipment_name: str
    service_description: str
    type_service: list
    task_list: list
    files: list
    user_id: int

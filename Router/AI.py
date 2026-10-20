from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.AI import AI
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
ai_router = APIRouter()

@ai_router.post('/ai/report-assistant', tags=["AI"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def report_assistant(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = AI(db).report_assistant(data)
    return response

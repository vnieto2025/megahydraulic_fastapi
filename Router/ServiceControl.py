from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.ServiceControl import ServiceControl
from Schemas.service_control import ServiceControl as ServiceControlSchema
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
service_control_router = APIRouter()


@service_control_router.post('/service_control/create', tags=["ServiceControl"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def create_service_control(request: Request, service_control: ServiceControlSchema, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ServiceControl(db).create_service_control(data)
    return response


@service_control_router.post('/service_control/list', tags=["ServiceControl"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def list_service_control(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ServiceControl(db).list_service_control(data)
    return response


@service_control_router.post('/service_control/get', tags=["ServiceControl"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_service_control(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ServiceControl(db).get_service_control(data)
    return response


@service_control_router.post('/service_control/update', tags=["ServiceControl"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def update_service_control(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ServiceControl(db).update_service_control(data)
    return response


@service_control_router.post('/service_control/convert_to_report', tags=["ServiceControl"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def convert_to_report(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = ServiceControl(db).convert_to_report(data)
    return response

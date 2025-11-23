from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Params import Param
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
param_router = APIRouter()

@param_router.post('/params/get_type_document', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_document(request: Request, db: Session = Depends(get_db)):
    response = Param(db).get_type_document()
    return response

@param_router.post('/params/get_type_user', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_user(request: Request, db: Session = Depends(get_db)):
    response = Param(db).get_type_user()
    return response

@param_router.post('/params/get_type_maintenance', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_maintenance(request: Request, db: Session = Depends(get_db)):
    response = Param(db).get_type_maintenance()
    return response

@param_router.post('/params/get_type_service', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_service(request: Request, db: Session = Depends(get_db)):
    response = Param(db).get_type_service()
    return response

@param_router.post('/params/get_type_equipments', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_equipments(request: Request, db: Session = Depends(get_db)):
    response = Param(db).get_type_equipments()
    return response

@param_router.post('/params/get_tasks_by_equipment', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_tasks_by_equipment(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Param(db).get_tasks_by_equipment(data)
    return response

@param_router.post('/params/get_lines_by_client', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_lines_by_client(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Param(db).get_lines_by_client(data)
    return response

@param_router.post('/params/get_users_by_client', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_users_by_client(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Param(db).get_users_by_client(data)
    return response

@param_router.post('/params/get_clients', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_clients(request: Request, db: Session = Depends(get_db)):
    response = Param(db).get_clients()
    return response
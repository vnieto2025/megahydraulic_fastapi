from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Params import Param
from Middleware.jwt_bearer import JWTBearer

tools = Tools()
param_router = APIRouter()

@param_router.post('/params/get_type_document', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_document(request: Request):
    response = Param().get_type_document()
    return response

@param_router.post('/params/get_type_user', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_user(request: Request):
    response = Param().get_type_user()
    return response

@param_router.post('/params/get_type_maintenance', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_maintenance(request: Request):
    response = Param().get_type_maintenance()
    return response

@param_router.post('/params/get_type_service', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_service(request: Request):
    response = Param().get_type_service()
    return response

@param_router.post('/params/get_type_equipments', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_type_equipments(request: Request):
    response = Param().get_type_equipments()
    return response

@param_router.post('/params/get_tasks_by_equipment', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_tasks_by_equipment(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Param().get_tasks_by_equipment(data)
    return response

@param_router.post('/params/get_lines_by_client', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_lines_by_client(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Param().get_lines_by_client(data)
    return response

@param_router.post('/params/get_users_by_client', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_users_by_client(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Param().get_users_by_client(data)
    return response

@param_router.post('/params/get_clients', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_clients(request: Request):
    response = Param().get_clients()
    return response
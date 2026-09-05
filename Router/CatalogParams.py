from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.CatalogParams import CatalogParams
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
catalog_params_router = APIRouter()

@catalog_params_router.post('/catalog_params/list', tags=["CatalogParams"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def list_catalog(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = CatalogParams(db).list_catalog(data)
    return response

@catalog_params_router.post('/catalog_params/create', tags=["CatalogParams"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def create_catalog(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = CatalogParams(db).create_catalog(data)
    return response

@catalog_params_router.post('/catalog_params/update', tags=["CatalogParams"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def update_catalog(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = CatalogParams(db).update_catalog(data)
    return response

@catalog_params_router.post('/catalog_params/toggle_status', tags=["CatalogParams"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def toggle_status(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = CatalogParams(db).toggle_status(data)
    return response

@catalog_params_router.post('/catalog_params/task_equipment_list', tags=["CatalogParams"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def list_task_equipment(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = CatalogParams(db).list_task_equipment(data)
    return response

@catalog_params_router.post('/catalog_params/task_equipment_toggle', tags=["CatalogParams"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def toggle_task_equipment(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = CatalogParams(db).toggle_task_equipment(data)
    return response

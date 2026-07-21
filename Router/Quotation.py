from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Quotation import Quotation
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
quotation_router = APIRouter()


@quotation_router.post('/quotation/get_plants', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_quotation_plants(request: Request, db: Session = Depends(get_db)):
    response = Quotation(db).get_plants()
    return response


@quotation_router.post('/quotation/get_labor_types', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_labor_types(request: Request, db: Session = Depends(get_db)):
    response = Quotation(db).get_labor_types()
    return response


@quotation_router.post('/quotation/create', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def create_quotation(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Quotation(db).create_quotation(data)
    return response


@quotation_router.post('/quotation/list', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def list_quotations(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Quotation(db).list_quotations(data)
    return response


@quotation_router.post('/quotation/get', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_quotation(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Quotation(db).get_quotation(data)
    return response


@quotation_router.post('/quotation/edit', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def edit_quotation(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Quotation(db).edit_quotation(data)
    return response


@quotation_router.post('/quotation/change_status', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def change_status_quotation(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Quotation(db).change_status_quotation(data)
    return response


@quotation_router.post('/quotation/delete_photo', tags=["Quotation"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def delete_quotation_photo(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Quotation(db).delete_quotation_photo(data)
    return response


@quotation_router.post('/quotation/generate_pdf', tags=["Quotation"], dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
def generate_quotation_pdf(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    return Quotation(db).generate_pdf(data)

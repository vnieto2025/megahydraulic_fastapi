from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Client import Client
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
client_router = APIRouter()

@client_router.post('/client/create', tags=["Client"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def create_client(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Client(db).create_client(data)
    return response

@client_router.post('/client/list_client', tags=["Client"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def list_client(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Client(db).list_client(data)
    return response

@client_router.post('/client/update_client', tags=["Client"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def update_client(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Client(db).update_client(data)
    return response

@client_router.post('/client/get_client', tags=["Client"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def get_client(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Client(db).get_client(data)
    return response

@client_router.post('/client/add_line_person', tags=["Client"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def add_line_person(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Client(db).add_line_person(data)
    return response
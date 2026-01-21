from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.User import User
from Schemas.user import User as UserSchema
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db
from sqlalchemy.orm import Session

tools = Tools()
user_router = APIRouter()

@user_router.post('/login', tags=["Auth"], response_model=dict)
@http_decorator
def login(request: Request, user: UserSchema, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).login(data)
    return response

@user_router.post('/user/get_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_user(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).get_user(data)
    return response

@user_router.post('/user/create_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def create_user(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).create_user(data)
    return response

@user_router.post('/user/update_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def update_user(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).update_user(data)
    return response

@user_router.post('/user/list_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def list_user(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).list_user(data)
    return response

@user_router.post('/user/change_status', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def change_status(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).change_status(data)
    return response

@user_router.post('/user/update_type_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def update_type_user(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).update_type_user(data)
    return response

@user_router.post('/user/change_password', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def change_password(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).change_password(data)
    return response

@user_router.post('/user/check_token', tags=["Auth"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def check_token(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint para verificar el tiempo restante del token.
    Retorna los minutos restantes antes de que expire.
    """
    # Obtener el token del header Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return tools.output(401, "Token no proporcionado", {})
    
    token = auth_header.split(" ")[1]
    
    # Llamar al método de la clase User
    response = User(db).check_token(token)
    return response

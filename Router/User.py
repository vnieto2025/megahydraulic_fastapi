from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.User import User
from Schemas.user import User as UserSchema
from Middleware.jwt_bearer import JWTBearer

tools = Tools()
user_router = APIRouter()

@user_router.post('/login', tags=["Auth"], response_model=dict)
@http_decorator
def login(request: Request, user: UserSchema):
    data = getattr(request.state, "json_data", {})
    response = User().login(data)
    return response

@user_router.post('/user/get_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def get_user(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().get_user(data)
    return response

@user_router.post('/user/create_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def create_user(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().create_user(data)
    return response

@user_router.post('/user/update_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def update_user(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().update_user(data)
    return response

@user_router.post('/user/list_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def list_user(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().list_user(data)
    return response

@user_router.post('/user/change_status', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def change_status(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().change_status(data)
    return response

@user_router.post('/user/update_type_user', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def update_type_user(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().update_type_user(data)
    return response

@user_router.post('/user/change_password', tags=["User"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def change_password(request: Request):
    data = getattr(request.state, "json_data", {})
    response = User().change_password(data)
    return response

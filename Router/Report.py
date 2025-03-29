from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Reports import Report
from Schemas.report import Report as ReportSchema
from Middleware.jwt_bearer import JWTBearer

tools = Tools()
report_router = APIRouter()

@report_router.post('/reports/create_report', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def create_report(request: Request, report: ReportSchema):
    data = getattr(request.state, "json_data", {})
    response = Report().create_report(data)
    return response

@report_router.post('/reports/generate_report', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def generate_report(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().generate_report(data)
    return response

@report_router.post('/reports/list_report', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def list_report(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().list_report(data)
    return response

@report_router.post('/reports/edit_report', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1, 2]))])
@http_decorator
def edit_report(request: Request, report: ReportSchema):
    data = getattr(request.state, "json_data", {})
    response = Report().edit_report(data)
    return response

@report_router.post('/reports/change_status_report', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def change_status_report(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().change_status_report(data)
    return response

@report_router.post('/reports/create_report_acesco', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def create_report_acesco(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().create_report_acesco(data)
    return response

@report_router.post('/reports/generate_report_acesco', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def generate_report_acesco(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().generate_report_acesco(data)
    return response

@report_router.post('/reports/list_report_acesco', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def list_report_acesco(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().list_report_acesco(data)
    return response

@report_router.post('/reports/edit_report_acesco', tags=["Reports"], response_model=dict, dependencies=[Depends(JWTBearer(required_roles=[1]))])
@http_decorator
def edit_report_acesco(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Report().edit_report_acesco(data)
    return response
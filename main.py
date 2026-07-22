from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from Config.db import BASE, engine
from Middleware.get_json import JSONMiddleware
from Router.User import user_router
from Router.Params import param_router
from Router.Report import report_router
from Router.Client import client_router
from Router.ServiceControl import service_control_router
from Router.Quotation import quotation_router
from pathlib import Path


route = Path.cwd()
app = FastAPI()
app.title = "Mega Hydraulic Project"
app.version = "0.0.1"

# Sirve la carpeta "assets" en la ruta "/assets"
app.mount("/assets", StaticFiles(directory=f"{route}/assets"), name="assets")
app.mount("/Uploads", StaticFiles(directory=f"{route}/Uploads"), name="Uploads")
app.add_middleware(JSONMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
app.include_router(user_router)
app.include_router(param_router)
app.include_router(report_router)
app.include_router(client_router)
app.include_router(service_control_router)
app.include_router(quotation_router)

BASE.metadata.create_all(bind=engine)

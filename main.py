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
from Models.quotation_plant_model import QuotationPlantModel
from Models.quotation_model import QuotationModel
from Models.quotation_item_model import QuotationItemModel
from Models.labor_type_model import LaborTypeModel
from Models.quotation_labor_model import QuotationLaborModel
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
    allow_origins=["*"],  # Permitir todos los orígenes; para producción, especifica los orígenes permitidos.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos; puedes especificar los métodos permitidos.
    allow_headers=["*"],  # Permitir todos los encabezados; puedes especificar los encabezados permitidos.
)
app.include_router(user_router)
app.include_router(param_router)
app.include_router(report_router)
app.include_router(client_router)
app.include_router(service_control_router)
app.include_router(quotation_router)

BASE.metadata.create_all(bind=engine)


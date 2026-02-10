from Models.logs_model import LogsModel
from .tools import CustomException, Tools
from .rules import Rules
from .querys import Querys
from functools import wraps
from fastapi import Request
from sqlalchemy import exc
import traceback
import json
from urllib.parse import urlparse
from fastapi.responses import StreamingResponse
from datetime import datetime

tool = Tools()

def http_decorator(func):
    @wraps(func)
    def decorador(*args, **kwargs):
        # Verificar si el método es POST o PUT
        request: Request = kwargs.get("request")
        data_log = dict()
        if request.method in ['POST', 'PUT']:
            codigo = 200
            data = {}
            resultado = ""
            # Verificar si la solicitud tiene un encabezado Content-Type válido
            if request.headers.get('accept') == 'application/json':
                try:
                    # Intentar cargar el cuerpo de la solicitud como JSON
                    # body = request.json()
                    body = getattr(request.state, "json_data", {})
                    path = str(request.url.path)
                    # Parsear la URL
                    parsed_url = urlparse(path)
                    # Obtener la ruta
                    path = parsed_url.path
                    Rules(path, body)
                    # Corre la función
                    resultado = func(*args, **kwargs)
                except CustomException as ce:
                    codigo = ce.codigo
                    message = ce.message
                    data = ce.data
                    resultado = tool.result(message, codigo,
                                            "CustomException", data)
                except json.JSONDecodeError as json_e:
                    print(str(json_e))
                    print(traceback.extract_tb(json_e.__traceback__))
                    codigo = 403
                    message = "La petición tiene un formato inválido."
                    resultado = tool.result(message, codigo, "JSONDecodeError")
                except KeyError as ke:
                    print(str(ke))
                    print(traceback.extract_tb(ke.__traceback__))
                    codigo = 422
                    message = f"Los datos enviados no son correctos o están incompletos. Verifique la información e inténtelo nuevamente. campo:{ke}"
                    resultado = tool.result(message, codigo, "KeyError")
                except TypeError as te:
                    print(str(te))
                    print(traceback.extract_tb(te.__traceback__))
                    codigo = 400
                    message = "Ha ocurrido un error al procesar los datos."
                    resultado = tool.result(message, codigo, "TypeError")
                except ValueError as ve:
                    print(str(ve))
                    print(traceback.extract_tb(ve.__traceback__))
                    codigo = 400
                    message = "Ha ocurrido un error al procesar los datos."
                    resultado = tool.result(message, codigo, "ValueError")
                except exc.OperationalError as te:
                    print(str(te))
                    print(traceback.extract_tb(te.__traceback__))
                    codigo = 500
                    message = "Hubo un error de conexión. Por favor intentelo más tarde."
                    resultado = tool.result(message, codigo, "OperationalError")
                except UnboundLocalError as ul:
                    print(str(ul))
                    print(traceback.extract_tb(ul.__traceback__))
                    codigo = 500
                    message = "Hubo un problema interno del sistema. Por favor intentelo más tarde."
                    resultado = tool.result(message, codigo, "UnboundLocalError")
                except Exception as ex:
                    print(str(ex))
                    print(traceback.extract_tb(ex.__traceback__))
                    codigo = 500
                    message = "Hubo un problema interno del sistema. Por favor intentelo más tarde."
                    resultado = tool.result(message, codigo, "Exception")
                finally:
                    if codigo != 200:
                        resultado = tool.output(codigo, message, data)

                    if isinstance(resultado, StreamingResponse):
                        if request.url.path in ["/reports/generate_report", "/reports/generate_report_acesco"]:
                            if "flag" in body and body["flag"]:
                                contenido = "IMPRIMIENDO PDF"
                            else:
                                contenido = "DESCARGANDO PDF"
                        elif request.url.path in ["/reports/generate_multiple_reports", "/reports/generate_multiple_reports_acesco"]:
                            contenido = "DESCARGANDO ZIP CON MÚLTIPLES PDFS"
                    else:
                        # Función para limpiar datos base64 de imágenes antes de guardar en logs
                        def clean_base64_data(obj, max_length=500):
                            """Elimina o trunca datos base64 de imágenes en el objeto"""
                            if isinstance(obj, dict):
                                cleaned = {}
                                for key, value in obj.items():
                                    # Eliminar campos conocidos de archivos
                                    if key in ["files", "file", "images", "image", "photos", "photo", "attachments"]:
                                        cleaned[key] = "[ARCHIVOS REMOVIDOS]"
                                    # Si es un string muy largo que parece base64, truncarlo
                                    elif isinstance(value, str) and len(value) > max_length and any(indicator in value for indicator in ["data:image", "/9j/", "iVBORw0KGgo"]):
                                        cleaned[key] = f"[BASE64_IMAGE_TRUNCATED - {len(value)} chars]"
                                    else:
                                        cleaned[key] = clean_base64_data(value, max_length)
                                return cleaned
                            elif isinstance(obj, list):
                                return [clean_base64_data(item, max_length) for item in obj]
                            elif isinstance(obj, str) and len(obj) > max_length and any(indicator in obj for indicator in ["data:image", "/9j/", "iVBORw0KGgo"]):
                                return f"[BASE64_IMAGE_TRUNCATED - {len(obj)} chars]"
                            else:
                                return obj
                        
                        if request.url.path in ["/reports/create_report", "/reports/edit_report", "/reports/create_report_acesco", "/reports/edit_report_acesco"]:
                            body = clean_base64_data(body)
                        
                        # Acceder al contenido del JSONResponse
                        contenido_serializado = resultado.body  # Esto está en formato bytes
                        contenido = json.loads(contenido_serializado.decode("utf-8"))  # Convertirlo a dict

                    data_log = {
                        "service": request.url.path,
                        "method": request.method,
                        "request": str(body),
                        "response": str(contenido),
                        "ip": request.client.host,
                        "created_at": datetime.now()
                    }
                    db = kwargs.get("db")
                    if db:
                        querys = Querys(db)
                        querys.insert_data(LogsModel, data_log)
 
            return resultado
    return decorador

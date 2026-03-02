from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Utils.filters import Filters
from Models.report_model import ReportModel
from Models.report_details_model import ReportDetailsModel
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from Models.client_user_model import ClientUserModel
from Models.type_service_model import TypeServiceModel
from Models.type_equipment_model import TypeEquipmentModel
from Models.task_list_model import TaskListModel
from Models.report_type_service_model import ReportTypeServiceModel
from Models.report_files_model import ReportFilesModel
from Models.report_attach_files_model import ReportAttachFilesModel
from Utils.rules import Rules
from datetime import datetime
import os
import base64
import uuid
import re
import io
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
import traceback
import zipfile

UPLOAD_FOLDER = "Uploads/"

class Report:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)
        self.filter_class = Filters()

    # Funcion for create a report
    def create_report(self, data):

        try:
            data_save = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "person_receives": data["person_receives"],
                "work_zone": None,
                "om": data["om"],
                "solped": data["solped"],
                "buy_order": data["buy_order"],
                "position": data["position"],
                "equipment_type_id": data["equipment_type_id"],
                "equipment_name": data["equipment_name"],
                "service_description": data["service_description"],
                "information": data["information"],
                "service_value": None,
                "conclutions": None,
                "recommendations": None,
                "tech_1": None,
                "tech_2": None,
                "type_report": 0,
                "user_id": data["user_id"]
            }

            self.querys.check_param_exists(
                ClientModel, 
                data["client_id"], 
                "Cliente"
            )

            self.querys.check_param_exists(
                ClientLinesModel, 
                data["client_line_id"], 
                "Línea"
            )

            self.querys.check_param_exists(
                ClientUserModel, 
                data["person_receives"], 
                "Persona que recibe"
            )

            self.querys.check_param_exists(
                TypeEquipmentModel, 
                data["equipment_type_id"], 
                "Tipo de equipo intervenido"
            )

            type_service = data["type_service"]
            if type_service:
                for index, type_s in enumerate(type_service):
                    Rules("/service_types", type_s)
                    self.querys.check_param_exists(
                        TypeServiceModel, 
                        type_s,
                        f"Tipo mantenimiento {index+1}"
                    )

            task_list = data["task_list"]
            if task_list:
                for index, task in enumerate(task_list):
                    Rules("/task_list", task)
                    self.querys.check_param_exists(
                        TaskListModel, 
                        task["task_id"],
                        f"Tarea {index+1}"
                    )

            id_report = self.querys.create_report(data_save)

            if type_service:
                for type_s in type_service:
                    data_type_service = {
                        "report_id": id_report,
                        "type_service_id": type_s,
                    }
                    self.querys.insert_data(
                        ReportTypeServiceModel, 
                        data_type_service
                    )

            if task_list:
                for task in task_list:
                    data_report_details_save = {
                        "report_id": id_report,
                        "task_id": task["task_id"],
                        "positive": task["positive"],
                        "negative": task["negative"],
                        "description": task["description"]
                    }
                    self.querys.insert_report_details(data_report_details_save)

            imagenes = data["files"]
            if imagenes:
                self.proccess_images(id_report, imagenes)

            return self.tools.output(201, "Reporte creado exitosamente.", id_report)

        except Exception as ex:
            raise CustomException(str(ex))

    # Function for process image files base64 and save them
    def proccess_images(self, id_report, imagenes):

        # Procesar y guardar cada archivo de la lista "files"
        for index, file_base64 in enumerate(imagenes):
            isbase64 = True if file_base64["img"].startswith("data:image/") else False

            if not isbase64:
                self.querys.find_image_and_update(id_report, file_base64)
                continue
                
            try:
                # Extraer el formato de la imagen
                file_extension = self.extract_file_extension(file_base64["img"])

                # Eliminar el prefijo base64 antes de decodificar
                base64_data = re.sub(r"^data:image/\w+;base64,", "", file_base64["img"])

                # Decodificar la imagen base64
                file_data = base64.b64decode(base64_data)

                # Open the image with Pillow
                image = Image.open(io.BytesIO(file_data))

                # Compress the image (resize or adjust quality)
                compressed_image_io = io.BytesIO()
                image = image.convert("RGB")  # Ensure the image is in RGB format (no alpha channel)
                
                # Save with compression
                image.save(
                    compressed_image_io,
                    format="JPEG",  # Convert to JPEG for better compression
                    optimize=True,
                    quality=75  # Adjust the quality (lower = more compression)
                )
                compressed_image_io.seek(0)
                compressed_data = compressed_image_io.read()

            except Exception as e:
                raise CustomException(f"Error al decodificar la imagen {index + 1}: {str(e)}")

            # Generar un nombre único para cada archivo
            file_name = f"{str(uuid.uuid4())}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Guardar la imagen decodificada en el servidor
            try:
                with open(file_path, "wb") as file:
                    file.write(compressed_data)
            except Exception as e:
                raise CustomException(f"Error al guardar la imagen {index + 1}: {str(e)}")

            data_save = {
                "report_id": id_report,
                "path": file_path,
                "description": file_base64["description"],
            }
            self.querys.insert_data(ReportFilesModel, data_save)

        return True
    
    # Busca el prefijo que indica el tipo de archivo, como data:image/jpeg;base64,
    def extract_file_extension(self, file_base64: str):
        match = re.match(r"data:image/(?P<ext>\w+);base64,", file_base64)
        if not match:
            raise ValueError("Formato de imagen no válido o prefijo faltante")
        
        # Extrae la extensión (jpg, png, etc.)
        return match.group("ext")

    # Function for generate pdf of the report
    def generate_report(self, data: dict):

        report_id = data["report_id"]
        flag = data.get("flag", False)

        data_report = self.querys.get_data_report(report_id)

        print("Data report para PDF:", data_report)  # Debug: Verificar los datos obtenidos

        # return self.tools.output(200, "Ok", data_report)
        # return self.tools.outputpdf(200, file_name, pdf)
        # Retornar el PDF como respuesta
        if flag:
            pdf = self.tools.gen_pdf(data_report)

            # Nombre del archivo pdf de salida
            file_name = f"reporte_{data['report_id']}_{str(datetime.now())}.pdf"

            return StreamingResponse(
                BytesIO(pdf),
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Type": "application/pdf",
                },
            )
        
        return self.tools.output(200, "Ok", data_report)

    # Function for list the reports
    def list_report(self, data: dict):
        
        message = "Información de reportes generado correctamente."
        limit = int(data["limit"])
        page_position = int(data["position"])
        state = data["state"]
        filters = data["filters"]
        user_id = int(data["user_id"])
        reports_dict = list()
        data_filter = list()
        response = list()

        filters = self.validate_filters(filters)
        if filters:
            data_filter = self.filter_class.get_filters(filters)

        if page_position <= 0:
            message = "El campo posición no es válido"
            raise CustomException(message)
        
        if state:
            reports = self.querys.list_reports(data, data_filter=data_filter)

        if not state:
            reports = self.querys.list_reports(
                data, 
                user_id, 
                state , 
                data_filter=data_filter
            )

        data_report = reports["reports"]
        reg_cont = reports["reg_cont"]

        if not data_report:
            message = "No hay listado de reportes que mostrar."
            return self.tools.output(200, message, data={
            "total_registros": 0,
            "total_pag": 0,
            "posicion_pag": 0,
            "reportes": []
        })

        for key in data_report:
            first_name = str(key.first_name).upper()
            last_name = str(key.last_name).upper()
            response.append({
                "id": key.id,
                "activity_date": key.activity_date,
                "client_name": key.client_name,
                "client_line": key.client_line,
                "person_receive_name": str(key.person_receive_name).upper(),
                "om": key.om,
                "solped": key.solped,
                "buy_order": key.buy_order,
                "position": key.position,
                # "type_equipment_name": key.type_equipment_name,
                "equipment_name": str(key.equipment_name).capitalize() if key.equipment_name else '',
                "user_name": f"{first_name} {last_name}"
            })

        if reg_cont%limit == 0:
            total_pag = reg_cont//limit
        else:
            total_pag = reg_cont//limit + 1

        if total_pag < int(page_position):
            message = "La posición excede el número total de registros."
            return self.tools.output(200, message, data={
            "total_registros": 0,
            "total_pag": 0,
            "posicion_pag": 0,
            "reportes": []
        })

        reports_dict = {
            "total_registros": reg_cont,
            "total_pag": total_pag,
            "posicion_pag": page_position,
            "reportes": response
        }

        return self.tools.output(200, message, reports_dict)

    # Function for edit existing reporte
    def edit_report(self, data: dict):
        
        try:
            data_save = {
                "report_id": data["report_id"],
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "person_receives": data["person_receives"],
                "om": data["om"],
                "solped": data["solped"],
                "buy_order": data["buy_order"],
                "position": data["position"],
                "equipment_type_id": data["equipment_type_id"],
                "equipment_name": data["equipment_name"],
                "service_description": data["service_description"],
                "information": data["information"],
                "user_id": data["user_id"]
            }

            self.querys.check_param_exists(
                ReportModel, 
                data["report_id"], 
                "Reporte"
            )

            self.querys.check_param_exists(
                ClientModel, 
                data["client_id"], 
                "Cliente"
            )

            self.querys.check_param_exists(
                ClientLinesModel, 
                data["client_line_id"], 
                "Línea"
            )

            self.querys.check_param_exists(
                ClientUserModel, 
                data["person_receives"], 
                "Persona que recibe"
            )

            self.querys.check_param_exists(
                TypeEquipmentModel, 
                data["equipment_type_id"], 
                "Tipo de equipo intervenido"
            )

            type_service = data["type_service"]
            if type_service:
                for index, type_s in enumerate(type_service):
                    Rules("/service_types", type_s)
                    self.querys.check_param_exists(
                        TypeServiceModel, 
                        type_s,
                        f"Tipo servicio {index+1}"
                    )

            task_list = data["task_list"]
            if task_list:
                for index, task in enumerate(task_list):
                    Rules("/task_list", task)
                    self.querys.check_param_exists(
                        TaskListModel, 
                        task["task_id"],
                        f"Tarea {index+1}"
                    )

            self.querys.edit_report(data_save)

            if type_service:
                self.querys.deactive_data(
                    ReportTypeServiceModel, 
                    data["report_id"]
                )
                for type_s in type_service:
                    data_type_service = {
                        "report_id": data["report_id"],
                        "type_service_id": type_s,
                    }
                    self.querys.insert_data(
                        ReportTypeServiceModel, 
                        data_type_service
                    )

            if task_list:
                self.querys.deactive_data(
                    ReportDetailsModel, 
                    data["report_id"]
                )
                for task in task_list:
                    data_report_details_save = {
                        "report_id": data["report_id"],
                        "task_id": task["task_id"],
                        "positive": task["positive"],
                        "negative": task["negative"],
                        "description": task["description"]
                    }
                    self.querys.insert_report_details(data_report_details_save)

            imagenes = data["files"]
            if imagenes:
                self.querys.deactive_data(ReportFilesModel, data["report_id"])
                self.proccess_images(data["report_id"], imagenes)
            else:
                self.querys.deactive_data(ReportFilesModel, data["report_id"])

            return self.tools.output(201, "Reporte editado exitosamente.", data["report_id"])

        except Exception as ex:
            raise CustomException(str(ex))

    # Function for verify if the values are empty
    def validate_filters(self, filters):
        if all(value == "" for value in filters.values()):
            return None
        return filters

    # Function for change status of report
    def change_status_report(self, data: dict):
        
        report_id = int(data["report_id"])

        self.querys.change_status_report(report_id)

        return self.tools.output(200, "Reporte eliminado con exito.")

    # Funcion for create a Acesco report
    def create_report_acesco(self, data):

        try:
            data_save = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "person_receives": data["person_receives"],
                "work_zone": data["work_zone"],
                "om": data["om"],
                "solped": data["solped"],
                "buy_order": data["buy_order"],
                "position": data["position"],
                "equipment_type_id": None,
                "equipment_name": None,
                "service_description": data["service_description"],
                "information": data["information"],
                "service_value": data["service_value"],
                "conclutions": data["conclutions"],
                "recommendations": data["recommendations"],
                "tech_1": data["tech_1"],
                "tech_2": data["tech_2"],
                "type_report": 1,
                "user_id": data["user_id"]
            }

            self.querys.check_param_exists(
                ClientModel, 
                data["client_id"], 
                "Cliente"
            )

            self.querys.check_param_exists(
                ClientLinesModel, 
                data["client_line_id"], 
                "Línea"
            )

            self.querys.check_param_exists(
                ClientUserModel, 
                data["person_receives"], 
                "Persona que recibe"
            )

            id_report = self.querys.create_report(data_save)

            imagenes = data["files"]
            if imagenes:
                self.proccess_images_acesco(id_report, imagenes)

            anexos = data["anexos"]
            if anexos:
                self.proccess_attachs_acesco(id_report, anexos)

            return self.tools.output(201, "Reporte creado exitosamente.", id_report)

        except Exception as ex:
            raise CustomException(str(ex))
  
    # Function for generate pdf of the acesco report
    def generate_report_acesco(self, data: dict):

        report_id = data["report_id"]
        flag = data.get("flag", False)

        data_report = self.querys.get_data_report_acesco(report_id)

        pdf = self.tools.gen_pdf_acesco(data_report)

        # Nombre del archivo pdf de salida
        file_name = f"reporte_acesco_{data['report_id']}_{str(datetime.now())}.pdf"

        # return self.tools.output(200, "Ok", data_report)
        # return self.tools.outputpdf(200, file_name, pdf)
        # Retornar el PDF como respuesta
        if flag:
            return StreamingResponse(
                BytesIO(pdf),
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Type": "application/pdf",
                },
            )
        
        return self.tools.output(200, "Ok", data_report)

    # Function for list the reports of acesco design
    def list_report_acesco(self, data: dict):
        
        message = "Información de reportes generado correctamente."
        limit = int(data["limit"])
        page_position = int(data["position"])
        state = data["state"]
        filters = data["filters"]
        user_id = int(data["user_id"])
        reports_dict = list()
        data_filter = list()
        response = list()

        filters = self.validate_filters(filters)
        if filters:
            data_filter = self.filter_class.get_filters(filters)

        if page_position <= 0:
            message = "El campo posición no es válido"
            raise CustomException(message)
        
        if state:
            reports = self.querys.list_reports_acesco(data, data_filter=data_filter)

        if not state:
            reports = self.querys.list_reports_acesco(
                data, 
                user_id, 
                state , 
                data_filter=data_filter
            )

        data_report = reports["reports"]
        reg_cont = reports["reg_cont"]

        if not data_report:
            message = "No hay listado de reportes que mostrar."
            return self.tools.output(200, message, data={
            "total_registros": 0,
            "total_pag": 0,
            "posicion_pag": 0,
            "reportes": []
        })

        for key in data_report:
            first_name = str(key.first_name).upper()
            last_name = str(key.last_name).upper()
            response.append({
                "id": key.id,
                "activity_date": key.activity_date,
                "client_name": key.client_name,
                "client_line": key.client_line,
                "person_receive_name": str(key.person_receive_name).upper(),
                "work_zone": key.work_zone,
                "om": key.om,
                "solped": key.solped,
                "buy_order": key.buy_order,
                "position": key.position,
                "user_name": f"{first_name} {last_name}"
            })

        if reg_cont%limit == 0:
            total_pag = reg_cont//limit
        else:
            total_pag = reg_cont//limit + 1

        if total_pag < int(page_position):
            message = "La posición excede el número total de registros."
            return self.tools.output(200, message, data={
            "total_registros": 0,
            "total_pag": 0,
            "posicion_pag": 0,
            "reportes": []
        })

        reports_dict = {
            "total_registros": reg_cont,
            "total_pag": total_pag,
            "posicion_pag": page_position,
            "reportes": response
        }

        return self.tools.output(200, message, reports_dict)

    # Function for edit existing reporte
    def edit_report_acesco(self, data: dict):
        
        try:
            data_save = {
                "report_id": data["report_id"],
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "person_receives": data["person_receives"],
                "work_zone": data["work_zone"],
                "om": data["om"],
                "solped": data["solped"],
                "buy_order": data["buy_order"],
                "position": data["position"],
                "service_description": data["service_description"],
                "information": data["information"],
                "service_value": data["service_value"],
                "conclutions": data["conclutions"],
                "recommendations": data["recommendations"],
                "tech_1": data["tech_1"],
                "tech_2": data["tech_2"],
                "user_id": data["user_id"]
            }

            self.querys.check_param_exists(
                ReportModel, 
                data["report_id"], 
                "Reporte"
            )

            self.querys.check_param_exists(
                ClientModel, 
                data["client_id"], 
                "Cliente"
            )

            self.querys.check_param_exists(
                ClientLinesModel, 
                data["client_line_id"], 
                "Línea"
            )

            self.querys.check_param_exists(
                ClientUserModel, 
                data["person_receives"], 
                "Persona que recibe"
            )

            self.querys.edit_report_acesco(data_save)

            imagenes = data["files"]
            if imagenes:
                self.querys.deactive_data(ReportFilesModel, data["report_id"])
                self.proccess_images_acesco(data["report_id"], imagenes)
            else:
                self.querys.deactive_data(ReportFilesModel, data["report_id"])

            anexos = data["anexos"]
            if anexos:
                self.querys.deactive_data(ReportAttachFilesModel, data["report_id"])
                self.proccess_attachs_acesco(data["report_id"], anexos)
            else:
                self.querys.deactive_data(ReportAttachFilesModel, data["report_id"])

            return self.tools.output(201, "Reporte editado exitosamente.", data["report_id"])

        except Exception as ex:
            traceback.print_exc()

            # O si prefieres guardar el traceback como string:
            error_trace = traceback.format_exc()
            print(error_trace)
            raise CustomException(str(ex))

    # Function for process image files base64 and save them
    def proccess_images_acesco(self, id_report, imagenes):

        # Procesar y guardar cada archivo de la lista "files"
        for index, file_base64 in enumerate(imagenes):

            isbase64 = True if file_base64.startswith("data:image/") else False

            if not isbase64:
                self.querys.find_image_and_update_version_two(ReportFilesModel, id_report, file_base64)
                continue
                
            try:
                # Extraer el formato de la imagen
                file_extension = self.extract_file_extension(file_base64)

                # Eliminar el prefijo base64 antes de decodificar
                base64_data = re.sub(r"^data:image/\w+;base64,", "", file_base64)

                # Decodificar la imagen base64
                file_data = base64.b64decode(base64_data)

                # Open the image with Pillow
                image = Image.open(io.BytesIO(file_data))

                # Compress the image (resize or adjust quality)
                compressed_image_io = io.BytesIO()
                image = image.convert("RGB")  # Ensure the image is in RGB format (no alpha channel)
                
                # Save with compression
                image.save(
                    compressed_image_io,
                    format="JPEG",  # Convert to JPEG for better compression
                    optimize=True,
                    quality=75  # Adjust the quality (lower = more compression)
                )
                compressed_image_io.seek(0)
                compressed_data = compressed_image_io.read()

            except Exception as e:
                print(e)
                raise CustomException(f"Error al decodificar la imagen {index + 1}: {str(e)}")

            # Generar un nombre único para cada archivo
            file_name = f"{str(uuid.uuid4())}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Guardar la imagen decodificada en el servidor
            try:
                with open(file_path, "wb") as file:
                    file.write(compressed_data)
            except Exception as e:
                print(e)
                raise CustomException(f"Error al guardar la imagen {index + 1}: {str(e)}")

            data_save = {
                "report_id": id_report,
                "path": file_path,
                "description": None,
            }
            self.querys.insert_data(ReportFilesModel, data_save)

        return True

    # Function for process image files base64 and save them
    def proccess_attachs_acesco(self, id_report, anexos):

        # Procesar y guardar cada archivo de la lista "files"
        for index, file_base64 in enumerate(anexos):

            isbase64 = True if file_base64.startswith("data:image/") else False

            if not isbase64:
                self.querys.find_image_and_update_version_two(ReportAttachFilesModel, id_report, file_base64)
                continue
                
            try:
                # Extraer el formato de la imagen
                file_extension = self.extract_file_extension(file_base64)

                # Eliminar el prefijo base64 antes de decodificar
                base64_data = re.sub(r"^data:image/\w+;base64,", "", file_base64)

                # Decodificar la imagen base64
                file_data = base64.b64decode(base64_data)

                # Open the image with Pillow
                image = Image.open(io.BytesIO(file_data))

                # Compress the image (resize or adjust quality)
                compressed_image_io = io.BytesIO()
                image = image.convert("RGB")  # Ensure the image is in RGB format (no alpha channel)
                
                # Save with compression
                image.save(
                    compressed_image_io,
                    format="JPEG",  # Convert to JPEG for better compression
                    optimize=True,
                    quality=75  # Adjust the quality (lower = more compression)
                )
                compressed_image_io.seek(0)
                compressed_data = compressed_image_io.read()

            except Exception as e:
                print(e)
                raise CustomException(f"Error al decodificar la imagen {index + 1}: {str(e)}")

            # Generar un nombre único para cada archivo
            file_name = f"{str(uuid.uuid4())}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Guardar la imagen decodificada en el servidor
            try:
                with open(file_path, "wb") as file:
                    file.write(compressed_data)
            except Exception as e:
                print(e)
                raise CustomException(f"Error al guardar la imagen {index + 1}: {str(e)}")

            data_save = {
                "report_id": id_report,
                "path": file_path
            }
            self.querys.insert_data(ReportAttachFilesModel, data_save)

        return True

    # Function for generate multiple reports PDFs
    def generate_multiple_reports(self, data: dict):
        try:
            report_ids = data.get("report_ids", [])
            
            if not report_ids:
                raise CustomException("No se proporcionaron IDs de reportes")
            
            if len(report_ids) > 50:
                raise CustomException("No se pueden generar más de 50 reportes a la vez")
            
            # Crear un archivo ZIP en memoria
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for report_id in report_ids:
                    try:
                        data_report = self.querys.get_data_report(report_id)
                        pdf_bytes = self.tools.gen_pdf(data_report)
                        
                        # Agregar el PDF al ZIP con un nombre único
                        pdf_filename = f"reporte_{report_id}.pdf"
                        zip_file.writestr(pdf_filename, pdf_bytes)
                        
                    except Exception as e:
                        print(f"Error generando reporte {report_id}: {str(e)}")
                        # Continuar con los demás reportes
                        continue
            
            # Preparar el buffer para la descarga
            zip_buffer.seek(0)
            
            # Nombre del archivo ZIP
            file_name = f"reportes_multiples_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.zip"
            
            return StreamingResponse(
                zip_buffer,
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Type": "application/zip",
                },
            )
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(traceback.format_exc())
            raise CustomException(f"Error al generar reportes múltiples: {str(e)}")

    # Function for generate multiple reports PDFs (Acesco)
    def generate_multiple_reports_acesco(self, data: dict):
        try:
            report_ids = data.get("report_ids", [])
            
            if not report_ids:
                raise CustomException("No se proporcionaron IDs de reportes")
            
            if len(report_ids) > 50:
                raise CustomException("No se pueden generar más de 50 reportes a la vez")
            
            # Crear un archivo ZIP en memoria
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for report_id in report_ids:
                    try:
                        data_report = self.querys.get_data_report_acesco(report_id)
                        pdf_bytes = self.tools.gen_pdf_acesco(data_report)
                        
                        # Agregar el PDF al ZIP con un nombre único
                        pdf_filename = f"reporte_acesco_{report_id}.pdf"
                        zip_file.writestr(pdf_filename, pdf_bytes)
                        
                    except Exception as e:
                        print(f"Error generando reporte Acesco {report_id}: {str(e)}")
                        # Continuar con los demás reportes
                        continue
            
            # Preparar el buffer para la descarga
            zip_buffer.seek(0)
            
            # Nombre del archivo ZIP
            file_name = f"reportes_acesco_multiples_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}.zip"
            
            return StreamingResponse(
                zip_buffer,
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}",
                    "Content-Type": "application/zip",
                },
            )
            
        except CustomException as e:
            raise e
        except Exception as e:
            print(traceback.format_exc())
            raise CustomException(f"Error al generar reportes Acesco múltiples: {str(e)}")

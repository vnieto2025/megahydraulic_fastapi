import base64
import io
import math
import os
import re
import traceback
import uuid
from datetime import datetime
from PIL import Image
from fastapi.responses import StreamingResponse
from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.quotation_model import QuotationModel
from Models.quotation_item_model import QuotationItemModel
from Models.quotation_labor_model import QuotationLaborModel
from Models.quotation_photos_model import QuotationPhotosModel
from Models.service_control_model import ServiceControlModel
from Class.QuotationPDF import QuotationPDF

UPLOAD_FOLDER = "Uploads/"


class Quotation:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)

    def process_images(self, quotation_id: int, fotos: list):
        for index, foto in enumerate(fotos):
            img_data = foto.get("img", "")
            if not img_data.startswith("data:image/"):
                continue
            try:
                match = re.search(r"data:image/(?P<ext>\w+);base64,", img_data)
                file_extension = match.group("ext") if match else "jpeg"
                base64_data = re.sub(r"^data:image/\w+;base64,", "", img_data)
                file_data = base64.b64decode(base64_data)
                image = Image.open(io.BytesIO(file_data))
                compressed_io = io.BytesIO()
                image = image.convert("RGB")
                image.save(compressed_io, format="JPEG", optimize=True, quality=75)
                compressed_io.seek(0)
                compressed_data = compressed_io.read()
            except Exception as e:
                raise CustomException(f"Error al procesar la imagen {index + 1}: {str(e)}")

            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            try:
                with open(file_path, "wb") as f:
                    f.write(compressed_data)
            except Exception as e:
                raise CustomException(f"Error al guardar la imagen {index + 1}: {str(e)}")

            self.querys.insert_data(QuotationPhotosModel, {
                "quotation_id": quotation_id,
                "path": file_path,
                "description": foto.get("description"),
            })

    def get_labor_types(self):
        try:
            labor_types = self.querys.get_labor_types()
            result = [
                {
                    "id": l.id,
                    "code": l.code,
                    "description": l.description,
                    "unit": l.unit,
                    "value": float(l.value),
                }
                for l in labor_types
            ]
            return self.tools.output(200, "Tipos de mano de obra obtenidos correctamente.", result)
        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def get_plants(self):
        try:
            plants = self.querys.get_quotation_plants()
            result = [
                {
                    "id": p.id,
                    "name": p.name,
                    "prefix": p.prefix,
                    "consecutive": p.consecutive,
                    "next_number": f"{p.prefix}-{p.consecutive:05d}",
                }
                for p in plants
            ]
            return self.tools.output(200, "Plantas obtenidas correctamente.", result)
        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def create_quotation(self, data: dict):
        try:
            if not data.get("client_line_id"):
                raise CustomException("Debe seleccionar una línea/área.")
            if not data.get("responsible_id"):
                raise CustomException("Debe seleccionar un interventor.")

            plant = self.querys.get_plant_for_update(int(data["plant_id"]))
            if not plant:
                raise CustomException("Planta no encontrada.")

            quotation_number = f"{plant.prefix}-{plant.consecutive:05d}"

            # Incrementar consecutivo de forma atómica antes de commit final
            plant.consecutive += 1

            data_save = {
                "plant_id": int(data["plant_id"]),
                "quotation_number": quotation_number,
                "city": data.get("city", "").strip() if data.get("city") else None,
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": int(data["client_id"]),
                "client_line_id": int(data["client_line_id"]) if data.get("client_line_id") else None,
                "responsible_id": int(data["responsible_id"]) if data.get("responsible_id") else None,
                "directed_to": data.get("directed_to", "").strip() if data.get("directed_to") else None,
                "phone": data.get("phone", "").strip() if data.get("phone") else None,
                "nit": data.get("nit", "").strip() if data.get("nit") else None,
                "component_id": int(data["component_id"]) if data.get("component_id") else None,
                "executed": int(data["executed"]) if data.get("executed") is not None else None,
                "scope": data.get("scope", "").strip() if data.get("scope") else None,
                "delivery_time": data.get("delivery_time", "").strip() if data.get("delivery_time") else None,
                "activity_description": data.get("activity_description", "").strip() if data.get("activity_description") else None,
                "execution_place": data.get("execution_place", "").strip() if data.get("execution_place") else None,
                "subtotal": float(data.get("subtotal", 0)),
                "subtotal_with_iva": float(data.get("subtotal_with_iva", 0)),
                "user_id": int(data["user_id"]),
            }
            quotation_id = self.querys.insert_data(QuotationModel, data_save)

            # Commit del consecutivo ya actualizado (insert_data hace commit,
            # pero plant sigue en la misma sesión — forzamos flush aquí)
            self.querys.db.commit()

            items = data.get("items", [])
            item_counter = 1
            for item in items:
                item_type = item.get("item_type", "item")
                item_data = {
                    "quotation_id": quotation_id,
                    "item_order": item_counter if item_type == "item" else None,
                    "sap_code": item.get("sap_code", "").strip() if item.get("sap_code") else None,
                    "description": item.get("description", "").strip() if item.get("description") else None,
                    "unit": item.get("unit", "").strip() if item.get("unit") else None,
                    "quantity": float(item.get("quantity", 0)),
                    "unit_price": float(item.get("unit_price", 0)),
                    "total_price": float(item.get("total_price", 0)),
                    "item_type": item_type,
                }
                self.querys.insert_data(QuotationItemModel, item_data)
                if item_type == "item":
                    item_counter += 1

            for labor in data.get("labor_items", []):
                self.querys.insert_data(QuotationLaborModel, {
                    "quotation_id": quotation_id,
                    "labor_type_id": int(labor["labor_type_id"]),
                    "quantity": float(labor.get("quantity", 0)),
                    "unit_price": float(labor.get("unit_price", 0)),
                    "total_price": float(labor.get("total_price", 0)),
                    "description": labor.get("description") or None,
                })

            for mat in data.get("material_items", []):
                qty = float(mat.get("quantity", 0))
                price = float(mat.get("unit_price", 0))
                self.querys.insert_data(QuotationItemModel, {
                    "quotation_id": quotation_id,
                    "sap_code": mat.get("sap_code") or None,
                    "description": mat.get("description") or None,
                    "unit": mat.get("unit") or None,
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": qty * price,
                    "row_description": mat.get("row_description") or None,
                    "item_type": "material",
                })

            for eq in data.get("equipment_items", []):
                qty = float(eq.get("quantity", 0))
                price = float(eq.get("unit_price", 0))
                self.querys.insert_data(QuotationItemModel, {
                    "quotation_id": quotation_id,
                    "description": eq.get("description") or None,
                    "unit": eq.get("unit") or None,
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": qty * price,
                    "row_description": eq.get("row_description") or None,
                    "item_type": "equipment",
                })

            for sur in data.get("hourly_surcharge_items", []):
                qty = float(sur.get("quantity", 0))
                price = float(sur.get("unit_price", 0))
                pct = float(sur.get("surcharge_percent", 0))
                self.querys.insert_data(QuotationItemModel, {
                    "quotation_id": quotation_id,
                    "description": sur.get("description") or None,
                    "unit": sur.get("unit") or None,
                    "quantity": qty,
                    "unit_price": price,
                    "surcharge_percent": pct,
                    "total_price": qty * price * (pct / 100) if pct else 0,
                    "row_description": sur.get("row_description") or None,
                    "item_type": "hourly_surcharge",
                })

            fotos = data.get("fotos", [])
            if fotos:
                self.process_images(quotation_id, fotos)

            # Crear control de servicio asociado automáticamente
            sc_data = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": int(data["client_id"]),
                "client_line_id": int(data["client_line_id"]),
                "responsible_id": int(data["responsible_id"]),
                "description": data.get("activity_description", "").strip() if data.get("activity_description") else None,
                "information": data.get("scope", "").strip() if data.get("scope") else None,
                "service_order": None,
                "quotation": quotation_number,
                "component": int(data["component_id"]) if data.get("component_id") else None,
                "component_quantity": 0,
                "value": float(data.get("subtotal", 0)),
                "solped": None,
                "oc": None,
                "position": None,
                "service_status": 5 if int(data.get("executed") or 0) == 1 else 1,
                "report_status": 0,
                "consecutive": None,
                "invoice": None,
                "invoice_date": None,
                "note": None,
                "hes": None,
                "gestor": None,
                "report_id": None,
                "user_id": int(data["user_id"]),
            }
            self.querys.insert_data(ServiceControlModel, sc_data)

            return self.tools.output(200, "Cotización creada correctamente.", {
                "quotation_id": quotation_id,
                "quotation_number": quotation_number,
            })

        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def get_quotation(self, data: dict):
        try:
            quotation_id = int(data["quotation_id"])
            detail = self.querys.get_quotation_detail(quotation_id)
            if not detail:
                raise CustomException("Cotización no encontrada.")

            h = detail["header"]
            items = detail["items"]

            response = {
                "id": h.id,
                "quotation_number": h.quotation_number,
                "plant_id": h.plant_id,
                "plant_name": h.plant_name,
                "city": h.city,
                "activity_date": str(h.activity_date),
                "client_id": h.client_id,
                "client_name": h.client_name,
                "client_line_id": h.client_line_id,
                "client_line_name": h.client_line_name,
                "responsible_id": h.responsible_id,
                "responsible_name": h.responsible_name,
                "directed_to": h.directed_to,
                "phone": h.phone,
                "nit": h.nit,
                "component_id": h.component_id,
                "component_name": h.component_name,
                "executed": h.executed,
                "scope": h.scope,
                "delivery_time": h.delivery_time,
                "activity_description": h.activity_description,
                "execution_place": h.execution_place,
                "subtotal": float(h.subtotal or 0),
                "subtotal_with_iva": float(h.subtotal_with_iva or 0),
                "items": [
                    {
                        "id": i.id,
                        "item_order": i.item_order,
                        "sap_code": i.sap_code,
                        "description": i.description,
                        "unit": i.unit,
                        "quantity": float(i.quantity),
                        "unit_price": float(i.unit_price),
                        "total_price": float(i.total_price),
                        "item_type": i.item_type,
                    }
                    for i in items if i.item_type in ("item", "logistics", "surcharge", "auto_labor", "auto_materials")
                ],
                "material_items": [
                    {
                        "id": i.id,
                        "sap_code": i.sap_code,
                        "description": i.description,
                        "unit": i.unit,
                        "quantity": float(i.quantity),
                        "unit_price": float(i.unit_price),
                        "total_price": float(i.total_price),
                        "row_description": i.row_description,
                    }
                    for i in items if i.item_type == "material"
                ],
                "equipment_items": [
                    {
                        "id": i.id,
                        "description": i.description,
                        "unit": i.unit,
                        "quantity": float(i.quantity),
                        "unit_price": float(i.unit_price),
                        "total_price": float(i.total_price),
                        "row_description": i.row_description,
                    }
                    for i in items if i.item_type == "equipment"
                ],
                "hourly_surcharge_items": [
                    {
                        "id": i.id,
                        "description": i.description,
                        "unit": i.unit,
                        "quantity": float(i.quantity),
                        "unit_price": float(i.unit_price),
                        "surcharge_percent": float(i.surcharge_percent or 0),
                        "total_price": float(i.total_price),
                        "row_description": i.row_description,
                    }
                    for i in items if i.item_type == "hourly_surcharge"
                ],
                "labor_items": [
                    {
                        "id": l.id,
                        "labor_type_id": l.labor_type_id,
                        "code": l.code,
                        "description": l.description,
                        "row_description": l.row_description,
                        "unit": l.unit,
                        "quantity": float(l.quantity),
                        "unit_price": float(l.unit_price),
                        "total_price": float(l.total_price),
                    }
                    for l in self.querys.get_quotation_labor(quotation_id)
                ],
                "photos": [
                    {
                        "id": p.id,
                        "path": p.path,
                        "description": p.description,
                    }
                    for p in self.querys.get_quotation_photos(quotation_id)
                ],
            }

            return self.tools.output(200, "Cotización obtenida correctamente.", response)

        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def edit_quotation(self, data: dict):
        try:
            quotation_id = int(data["quotation_id"])

            data_update = {
                "city": data.get("city") or None,
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": int(data["client_id"]),
                "client_line_id": int(data["client_line_id"]) if data.get("client_line_id") else None,
                "responsible_id": int(data["responsible_id"]) if data.get("responsible_id") else None,
                "directed_to": data.get("directed_to") or None,
                "phone": data.get("phone") or None,
                "nit": data.get("nit") or None,
                "component_id": int(data["component_id"]) if data.get("component_id") else None,
                "executed": int(data["executed"]) if data.get("executed") is not None else None,
                "scope": data.get("scope") or None,
                "delivery_time": data.get("delivery_time") or None,
                "activity_description": data.get("activity_description") or None,
                "execution_place": data.get("execution_place") or None,
                "subtotal": float(data.get("subtotal", 0)),
                "subtotal_with_iva": float(data.get("subtotal_with_iva", 0)),
                "updated_at": datetime.now(),
            }
            self.querys.update_quotation(quotation_id, data_update)

            self.querys.deactivate_quotation_items(quotation_id)
            items = data.get("items", [])
            item_counter = 1
            for item in items:
                item_type = item.get("item_type", "item")
                item_data = {
                    "quotation_id": quotation_id,
                    "item_order": item_counter if item_type == "item" else None,
                    "sap_code": item.get("sap_code") or None,
                    "description": item.get("description") or None,
                    "unit": item.get("unit") or None,
                    "quantity": float(item.get("quantity", 0)),
                    "unit_price": float(item.get("unit_price", 0)),
                    "total_price": float(item.get("total_price", 0)),
                    "item_type": item_type,
                }
                self.querys.insert_data(QuotationItemModel, item_data)
                if item_type == "item":
                    item_counter += 1

            self.querys.deactivate_quotation_labor(quotation_id)
            for labor in data.get("labor_items", []):
                self.querys.insert_data(QuotationLaborModel, {
                    "quotation_id": quotation_id,
                    "labor_type_id": int(labor["labor_type_id"]),
                    "quantity": float(labor.get("quantity", 0)),
                    "unit_price": float(labor.get("unit_price", 0)),
                    "total_price": float(labor.get("total_price", 0)),
                    "description": labor.get("description") or None,
                })

            for mat in data.get("material_items", []):
                qty = float(mat.get("quantity", 0))
                price = float(mat.get("unit_price", 0))
                self.querys.insert_data(QuotationItemModel, {
                    "quotation_id": quotation_id,
                    "sap_code": mat.get("sap_code") or None,
                    "description": mat.get("description") or None,
                    "unit": mat.get("unit") or None,
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": qty * price,
                    "row_description": mat.get("row_description") or None,
                    "item_type": "material",
                })

            for eq in data.get("equipment_items", []):
                qty = float(eq.get("quantity", 0))
                price = float(eq.get("unit_price", 0))
                self.querys.insert_data(QuotationItemModel, {
                    "quotation_id": quotation_id,
                    "description": eq.get("description") or None,
                    "unit": eq.get("unit") or None,
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": qty * price,
                    "row_description": eq.get("row_description") or None,
                    "item_type": "equipment",
                })

            for sur in data.get("hourly_surcharge_items", []):
                qty = float(sur.get("quantity", 0))
                price = float(sur.get("unit_price", 0))
                pct = float(sur.get("surcharge_percent", 0))
                self.querys.insert_data(QuotationItemModel, {
                    "quotation_id": quotation_id,
                    "description": sur.get("description") or None,
                    "unit": sur.get("unit") or None,
                    "quantity": qty,
                    "unit_price": price,
                    "surcharge_percent": pct,
                    "total_price": qty * price * (pct / 100) if pct else 0,
                    "row_description": sur.get("row_description") or None,
                    "item_type": "hourly_surcharge",
                })

            fotos_nuevas = data.get("fotos_nuevas", [])
            if fotos_nuevas:
                self.process_images(quotation_id, fotos_nuevas)

            return self.tools.output(200, "Cotización actualizada correctamente.", {"quotation_id": quotation_id})

        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def change_status_quotation(self, data: dict):
        try:
            quotation_id = int(data["quotation_id"])
            self.querys.change_status_quotation(quotation_id)
            return self.tools.output(200, "Cotización eliminada correctamente.")
        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def delete_quotation_photo(self, data: dict):
        try:
            photo_id = int(data["photo_id"])
            self.querys.delete_quotation_photo(photo_id)
            return self.tools.output(200, "Foto eliminada correctamente.")
        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def generate_pdf(self, data: dict):
        try:
            quotation_id = int(data["quotation_id"])
            result = self.get_quotation({"quotation_id": quotation_id})
            q_data = result.body  # JSONResponse bytes
            import json
            q_data = json.loads(q_data)["data"]

            pdf_bytes = QuotationPDF(q_data).generate()
            number = q_data.get("quotation_number", f"COT-{quotation_id}")
            filename = f"Cotizacion_{number}.pdf"
            from io import BytesIO
            return StreamingResponse(
                BytesIO(pdf_bytes),
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/pdf",
                },
            )
        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

    def list_quotations(self, data: dict):
        try:
            limit = int(data["limit"])
            page_position = int(data["position"])
            filters = data.get("filters", {})

            if page_position <= 0:
                raise CustomException("El campo posición no es válido")

            result = self.querys.list_quotations(data, filters)
            quotations = result["quotations"]
            reg_cont = result["reg_cont"]

            if not reg_cont:
                return self.tools.output(200, "No hay cotizaciones que mostrar.", data={
                    "total_registros": 0,
                    "total_pag": 0,
                    "posicion_pag": 0,
                    "quotations": []
                })

            total_pag = math.ceil(reg_cont / limit)
            response = []
            for q in quotations:
                response.append({
                    "id": q.id,
                    "quotation_number": q.quotation_number,
                    "city": q.city,
                    "activity_date": str(q.activity_date),
                    "client_name": q.client_name,
                    "client_line_name": q.client_line_name,
                    "responsible_name": q.responsible_name,
                    "plant_name": q.plant_name,
                    "subtotal": float(q.subtotal or 0),
                    "subtotal_with_iva": float(q.subtotal_with_iva or 0),
                    "user_name": f"{q.first_name} {q.last_name}".upper(),
                })

            return self.tools.output(200, "Listado de cotizaciones obtenido correctamente.", data={
                "total_registros": reg_cont,
                "total_pag": total_pag,
                "posicion_pag": page_position,
                "quotations": response
            })

        except CustomException as ex:
            raise ex
        except Exception as ex:
            traceback.print_exc()
            raise CustomException(str(ex))

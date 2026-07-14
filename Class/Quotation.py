import math
from datetime import datetime
from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.quotation_model import QuotationModel
from Models.quotation_item_model import QuotationItemModel


class Quotation:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)

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
            raise CustomException(str(ex))

    def create_quotation(self, data: dict):
        try:
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
                "phone": data.get("phone", "").strip() if data.get("phone") else None,
                "nit": data.get("nit", "").strip() if data.get("nit") else None,
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

            return self.tools.output(200, "Cotización creada correctamente.", {
                "quotation_id": quotation_id,
                "quotation_number": quotation_number,
            })

        except CustomException as ex:
            raise ex
        except Exception as ex:
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
                "phone": h.phone,
                "nit": h.nit,
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
                    for i in items
                ],
            }

            return self.tools.output(200, "Cotización obtenida correctamente.", response)

        except CustomException as ex:
            raise ex
        except Exception as ex:
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
                "phone": data.get("phone") or None,
                "nit": data.get("nit") or None,
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

            return self.tools.output(200, "Cotización actualizada correctamente.", {"quotation_id": quotation_id})

        except CustomException as ex:
            raise ex
        except Exception as ex:
            raise CustomException(str(ex))

    def change_status_quotation(self, data: dict):
        try:
            quotation_id = int(data["quotation_id"])
            self.querys.change_status_quotation(quotation_id)
            return self.tools.output(200, "Cotización eliminada correctamente.")
        except CustomException as ex:
            raise ex
        except Exception as ex:
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
            raise CustomException(str(ex))

from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.service_control_model import ServiceControlModel
from Models.report_model import ReportModel
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from datetime import datetime


class ServiceControl:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)

    def create_service_control(self, data: dict):

        try:
            data_save = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "responsible_id": data["responsible_id"],
                "description": data.get("description"),
                "information": data.get("information"),
                "service_order": data.get("service_order"),
                "quotation": data.get("quotation"),
                "component": data["component"],
                "component_quantity": data.get("component_quantity"),
                "value": data.get("value"),
                "solped": data.get("solped"),
                "oc": data.get("oc"),
                "position": data.get("position"),
                "service_status": data["service_status"],
                "report_status": data["report_status"],
                "consecutive": data.get("consecutive"),
                "invoice": data.get("invoice"),
                "invoice_date": self.tools.format_date(data["invoice_date"]) if data.get("invoice_date") else None,
                "note": data.get("note"),
                "report_id": data.get("report_id"),
                "user_id": data["user_id"],
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

            self.querys.insert_data(ServiceControlModel, data_save)

            return self.tools.output(201, "Control de servicio guardado correctamente.")

        except CustomException as ex:
            raise ex
        except Exception as ex:
            raise CustomException(str(ex))

    def get_service_control(self, data: dict):

        record_id = data["record_id"]
        component_labels = {0: "Hidráulico", 1: "Suministro", 2: "Mecánico"}

        key = self.querys.get_service_control(record_id)

        result = {
            "id": key.id,
            "activity_date": str(key.activity_date),
            "client_id": key.client_id,
            "client_name": key.client_name,
            "client_line_id": key.client_line_id,
            "client_line": key.client_line,
            "responsible_id": key.responsible_id,
            "description": key.description,
            "information": key.information,
            "service_order": key.service_order,
            "quotation": key.quotation,
            "component": key.component,
            "component_quantity": key.component_quantity,
            "value": float(key.value) if key.value else 0,
            "solped": key.solped,
            "oc": key.oc,
            "position": key.position,
            "service_status": key.service_status,
            "service_status_name": key.service_status_name,
            "report_status": key.report_status,
            "report_status_name": key.report_status_name,
            "consecutive": key.consecutive,
            "invoice": key.invoice,
            "invoice_date": str(key.invoice_date) if key.invoice_date else None,
            "note": key.note,
            "report_id": key.report_id,
            "user_id": key.user_id,
        }

        return self.tools.output(200, "Ok.", result)

    def update_service_control(self, data: dict):
        try:
            record_id = data["record_id"]

            self.querys.check_param_exists(
                ServiceControlModel,
                record_id,
                "Control de servicio"
            )

            data_update = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "responsible_id": data["responsible_id"],
                "description": data.get("description"),
                "information": data.get("information"),
                "service_order": data.get("service_order"),
                "quotation": data.get("quotation"),
                "component": data["component"],
                "component_quantity": data.get("component_quantity"),
                "value": data.get("value"),
                "solped": data.get("solped"),
                "oc": data.get("oc"),
                "position": data.get("position"),
                "service_status": data["service_status"],
                "report_status": data["report_status"],
                "consecutive": data.get("consecutive"),
                "invoice": data.get("invoice"),
                "invoice_date": self.tools.format_date(data["invoice_date"]) if data.get("invoice_date") else None,
                "note": data.get("note"),
                "user_id": data["user_id"],
            }

            self.querys.update_service_control(record_id, data_update)

            return self.tools.output(200, "Control de servicio actualizado correctamente.")

        except CustomException as ex:
            raise ex
        except Exception as ex:
            raise CustomException(str(ex))

    def list_service_control(self, data: dict):

        message = "Listado de controles de servicio generado correctamente."
        limit = int(data["limit"])
        page_position = int(data["position"])
        filters = data.get("filters", {})
        data_filter = []

        if page_position <= 0:
            raise CustomException("El campo posición no es válido")

        # Filtro por rango de fechas (el frontend envía YYYY-MM-DD)
        if filters.get("start_date"):
            start = datetime.strptime(filters["start_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date >= start)

        if filters.get("end_date"):
            end = datetime.strptime(filters["end_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date <= end)

        # Filtro multi-opción por service_status
        if filters.get("service_status") and len(filters["service_status"]) > 0:
            data_filter.append(ServiceControlModel.service_status.in_(filters["service_status"]))

        result = self.querys.list_service_controls(data, data_filter=data_filter)
        data_records = result["records"]
        reg_cont = result["reg_cont"]
        total_valor = float(result.get("total_valor", 0))
        total_valor_formateado = f"${total_valor:,.0f}".replace(",", ".")

        if not reg_cont:
            return self.tools.output(200, "No hay registros que mostrar.", data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

        response = []
        for key in data_records:
            valor = float(key.value) if key.value else 0
            response.append({
                "id": key.id,
                "activity_date": str(key.activity_date),
                "client_name": key.client_name,
                "client_line": key.client_line,
                "responsible": key.responsible_name,
                "service_order": key.service_order,
                "quotation": key.quotation,
                "component": key.component,
                "component_name": key.component_name if key.component is not None else '-',
                "component_quantity": key.component_quantity,
                "value": valor,
                "valor_formateado": f"${valor:,.0f}".replace(",", "."),
                "solped": key.solped,
                "oc": key.oc,
                "position": key.position,
                "service_status": key.service_status,
                "service_status_name": key.service_status_name,
                "report_status_name": key.report_status_name,
                "consecutive": key.consecutive,
                "invoice": key.invoice,
                "invoice_date": str(key.invoice_date) if key.invoice_date else None,
                "report_id": key.report_id,
            })

        if reg_cont % limit == 0:
            total_pag = reg_cont // limit
        else:
            total_pag = reg_cont // limit + 1

        if total_pag < page_position:
            return self.tools.output(200, "La posición excede el número total de registros.", data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

        return self.tools.output(200, message, {
            "total_registros": reg_cont,
            "total_pag": total_pag,
            "posicion_pag": page_position,
            "total_valor": total_valor,
            "total_valor_formateado": total_valor_formateado,
            "registros": response
        })

    def convert_to_report(self, data: dict):
        try:
            record_id = data["record_id"]

            sc = self.querys.get_service_control(record_id)
            if not sc:
                raise CustomException("Control de servicio no encontrado.")

            if sc.report_id:
                raise CustomException("Este control de servicio ya fue convertido en reporte (reporte #" + str(sc.report_id) + ").")

            type_report = 1 if sc.client_id == 1 else 0

            activity_dt = datetime.combine(sc.activity_date, datetime.min.time()) if sc.activity_date else datetime.now()

            report_data = {
                "activity_date": activity_dt,
                "client_id": sc.client_id,
                "client_line_id": sc.client_line_id,
                "person_receives": sc.responsible_id,
                "work_zone": None,
                "om": sc.service_order or None,
                "solped": sc.solped or None,
                "buy_order": sc.oc or None,
                "position": sc.position or None,
                "equipment_type_id": None,
                "equipment_name": None,
                "service_description": sc.description or "",
                "information": sc.information or "",
                "service_value": sc.value or 0,
                "conclutions": None,
                "recommendations": None,
                "tech_1": None,
                "tech_2": None,
                "type_report": type_report,
                "user_id": sc.user_id,
            }

            new_report_id = self.querys.insert_data(ReportModel, report_data)

            print("Nuevo report_id generado:", new_report_id)

            self.querys.update_service_control(record_id, {
                "report_id": new_report_id,
                "consecutive": new_report_id,
            })

            return self.tools.output(200, "Reporte creado exitosamente.", {"report_id": new_report_id})

        except CustomException as ex:
            raise ex
        except Exception as ex:
            raise CustomException(str(ex))

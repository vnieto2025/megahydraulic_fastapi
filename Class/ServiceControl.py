from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.service_control_model import ServiceControlModel
from Models.report_model import ReportModel
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from Models.client_user_model import ClientUserModel
from datetime import datetime
from sqlalchemy import or_
import traceback


class ServiceControl:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)

    def change_status(self, data: dict):
        try:
            record_id = data["record_id"]

            self.querys.check_param_exists(
                ServiceControlModel,
                record_id,
                "Control de servicio"
            )

            self.querys.change_status_service_control(record_id)

            return self.tools.output(200, f"Registro #{record_id} eliminado correctamente.")

        except CustomException as ex:
            raise ex
        except Exception as ex:
            raise CustomException(str(ex))

    def create_service_control(self, data: dict):

        try:
            data_save = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "responsible_id": data["responsible_id"],
                "description": data.get("description").strip() if data.get("description") else None,
                "information": data.get("information").strip() if data.get("information") else None,
                "service_order": data.get("service_order").strip() if data.get("service_order") else None,
                "quotation": data.get("quotation").strip() if data.get("quotation") else None,
                "component": data["component"],
                "component_quantity": data.get("component_quantity"),
                "value": data.get("value"),
                "solped": data.get("solped").strip() if data.get("solped") else None,
                "oc": data.get("oc").strip() if data.get("oc") else None,
                "position": data.get("position").strip() if data.get("position") else None,
                "service_status": data["service_status"],
                "report_status": data["report_status"],
                "consecutive": data.get("consecutive"),
                "invoice": data.get("invoice"),
                "invoice_date": self.tools.format_date(data["invoice_date"]) if data.get("invoice_date") else None,
                "note": data.get("note").strip() if data.get("note") else None,
                "hes": data.get("hes").strip() if data.get("hes") else None,
                "gestor": data.get("gestor").strip() if data.get("gestor") else None,
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

            if data_save.get("solped") and data_save.get("position"):
                duplicate = self.querys.check_solped_position_duplicate(
                    data_save["solped"],
                    data_save["position"]
                )
                if duplicate:
                    raise CustomException(
                        f"Ya existe un registro con la SOLPED '{data_save['solped']}' y posición '{data_save['position']}' (ID: {duplicate.id})."
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
            "hes": key.hes,
            "gestor": key.gestor,
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
                "description": data.get("description").strip() if data.get("description") else None,
                "information": data.get("information").strip() if data.get("information") else None,
                "service_order": data.get("service_order").strip() if data.get("service_order") else None,
                "quotation": data.get("quotation").strip() if data.get("quotation") else None,
                "component": data["component"],
                "component_quantity": data.get("component_quantity"),
                "value": data.get("value"),
                "solped": data.get("solped").strip() if data.get("solped") else None,
                "oc": data.get("oc").strip() if data.get("oc") else None,
                "position": data.get("position").strip() if data.get("position") else None,
                "service_status": data["service_status"],
                "report_status": data["report_status"],
                "consecutive": data.get("consecutive"),
                "invoice": data.get("invoice"),
                "invoice_date": self.tools.format_date(data["invoice_date"]) if data.get("invoice_date") else None,
                "note": data.get("note").strip() if data.get("note") else None,
                "hes": data.get("hes").strip() if data.get("hes") else None,
                "gestor": data.get("gestor").strip() if data.get("gestor") else None,
                "user_id": data["user_id"],
            }

            if data_update.get("solped") and data_update.get("position"):
                duplicate = self.querys.check_solped_position_duplicate(
                    data_update["solped"],
                    data_update["position"],
                    exclude_id=record_id
                )
                if duplicate:
                    raise CustomException(
                        f"Ya existe un registro con la SOLPED '{data_update['solped']}' y posición '{data_update['position']}' (ID: {duplicate.id})."
                    )

            self.querys.update_service_control(record_id, data_update)

            # Si el registro tiene un reporte asociado, sincronizar campos comunes
            sc_record = self.querys.get_service_control(record_id)
            if sc_record and sc_record.report_id:
                try:
                    self.querys.sync_report_fields_from_sc(sc_record.report_id, data_update)
                except Exception as sync_ex:
                    traceback.print_exc()
                    print(f"[sync_report_on_sc_edit] Error: {str(sync_ex)}")

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

        # Filtro multi-valor por solped (con soporte para vacíos)
        solped_values = filters.get("solped") or []
        if len(solped_values) > 0:
            has_empty_sp = "__EMPTY__" in solped_values
            real_sp = [v for v in solped_values if v != "__EMPTY__"]
            if has_empty_sp and real_sp:
                data_filter.append(or_(
                    ServiceControlModel.solped.in_(real_sp),
                    ServiceControlModel.solped == None,
                    ServiceControlModel.solped == ''
                ))
            elif has_empty_sp:
                data_filter.append(or_(
                    ServiceControlModel.solped == None,
                    ServiceControlModel.solped == ''
                ))
            elif real_sp:
                data_filter.append(ServiceControlModel.solped.in_(real_sp))

        # Filtro por cliente
        if filters.get("client_id"):
            data_filter.append(ServiceControlModel.client_id == int(filters["client_id"]))

        # Filtro por línea
        if filters.get("client_line_id"):
            data_filter.append(ServiceControlModel.client_line_id == int(filters["client_line_id"]))

        # Filtro por responsable
        if filters.get("responsible_id"):
            data_filter.append(ServiceControlModel.responsible_id == int(filters["responsible_id"]))

        # Filtro multi-opción por report_status
        if filters.get("report_status") and len(filters["report_status"]) > 0:
            data_filter.append(ServiceControlModel.report_status.in_(filters["report_status"]))

        # Filtro por consecutivo
        if filters.get("consecutive"):
            data_filter.append(ServiceControlModel.consecutive == int(filters["consecutive"]))

        # Filtro por HES (multi-valor)
        if filters.get("hes") and len(filters["hes"]) > 0:
            data_filter.append(ServiceControlModel.hes.in_(filters["hes"]))

        # Filtro por OC (multi-valor con soporte para vacíos)
        if filters.get("oc") and len(filters["oc"]) > 0:
            oc_values = filters["oc"]
            has_empty = "__EMPTY__" in oc_values
            real_values = [v for v in oc_values if v != "__EMPTY__"]
            if has_empty and real_values:
                data_filter.append(or_(
                    ServiceControlModel.oc.in_(real_values),
                    ServiceControlModel.oc == None,
                    ServiceControlModel.oc == ''
                ))
            elif has_empty:
                data_filter.append(or_(
                    ServiceControlModel.oc == None,
                    ServiceControlModel.oc == ''
                ))
            elif real_values:
                data_filter.append(ServiceControlModel.oc.in_(real_values))

        # Filtro por factura (invoice)
        if filters.get("factura"):
            try:
                data_filter.append(ServiceControlModel.invoice == int(filters["factura"]))
            except (ValueError, TypeError):
                pass

        # Filtro por rango de fecha de facturación
        if filters.get("invoice_date_start"):
            inv_start = datetime.strptime(filters["invoice_date_start"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date >= inv_start)

        if filters.get("invoice_date_end"):
            inv_end = datetime.strptime(filters["invoice_date_end"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date <= inv_end)

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
                "description": key.description,
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
                "hes": key.hes,
                "position": key.position,
                "service_status": key.service_status,
                "service_status_name": key.service_status_name,
                "report_status": key.report_status,
                "report_status_name": key.report_status_name,
                "consecutive": key.consecutive,
                "invoice": key.invoice,
                "invoice_date": str(key.invoice_date) if key.invoice_date else None,
                "report_id": key.report_id,
                "type_report": key.type_report,
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

    def get_oc_list(self, data: dict):
        filters = data.get("filters", {})
        data_filter = []

        if filters.get("start_date"):
            start = datetime.strptime(filters["start_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date >= start)

        if filters.get("end_date"):
            end = datetime.strptime(filters["end_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date <= end)

        if filters.get("service_status") and len(filters["service_status"]) > 0:
            data_filter.append(ServiceControlModel.service_status.in_(filters["service_status"]))

        if filters.get("report_status") and len(filters["report_status"]) > 0:
            data_filter.append(ServiceControlModel.report_status.in_(filters["report_status"]))

        solped_values = filters.get("solped") or []
        if len(solped_values) > 0:
            has_empty_sp = "__EMPTY__" in solped_values
            real_sp = [v for v in solped_values if v != "__EMPTY__"]
            if has_empty_sp and real_sp:
                data_filter.append(or_(
                    ServiceControlModel.solped.in_(real_sp),
                    ServiceControlModel.solped == None,
                    ServiceControlModel.solped == ''
                ))
            elif has_empty_sp:
                data_filter.append(or_(
                    ServiceControlModel.solped == None,
                    ServiceControlModel.solped == ''
                ))
            elif real_sp:
                data_filter.append(ServiceControlModel.solped.in_(real_sp))

        if filters.get("client_id"):
            data_filter.append(ServiceControlModel.client_id == int(filters["client_id"]))

        if filters.get("client_line_id"):
            data_filter.append(ServiceControlModel.client_line_id == int(filters["client_line_id"]))

        if filters.get("responsible_id"):
            data_filter.append(ServiceControlModel.responsible_id == int(filters["responsible_id"]))

        if filters.get("consecutive"):
            data_filter.append(ServiceControlModel.consecutive == int(filters["consecutive"]))

        if filters.get("hes") and len(filters["hes"]) > 0:
            data_filter.append(ServiceControlModel.hes.in_(filters["hes"]))

        if filters.get("factura"):
            try:
                data_filter.append(ServiceControlModel.invoice == int(filters["factura"]))
            except (ValueError, TypeError):
                pass

        # Filtro por rango de fecha de facturación
        if filters.get("invoice_date_start"):
            inv_start = datetime.strptime(filters["invoice_date_start"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date >= inv_start)

        if filters.get("invoice_date_end"):
            inv_end = datetime.strptime(filters["invoice_date_end"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date <= inv_end)

        oc_list = self.querys.get_unique_oc_list(data_filter=data_filter)
        return self.tools.output(200, "Ok.", oc_list)

    def get_hes_list(self, data: dict):
        filters = data.get("filters", {})
        data_filter = []

        if filters.get("start_date"):
            start = datetime.strptime(filters["start_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date >= start)

        if filters.get("end_date"):
            end = datetime.strptime(filters["end_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date <= end)

        if filters.get("service_status") and len(filters["service_status"]) > 0:
            data_filter.append(ServiceControlModel.service_status.in_(filters["service_status"]))

        if filters.get("report_status") and len(filters["report_status"]) > 0:
            data_filter.append(ServiceControlModel.report_status.in_(filters["report_status"]))

        solped_values = filters.get("solped") or []
        if len(solped_values) > 0:
            has_empty_sp = "__EMPTY__" in solped_values
            real_sp = [v for v in solped_values if v != "__EMPTY__"]
            if has_empty_sp and real_sp:
                data_filter.append(or_(
                    ServiceControlModel.solped.in_(real_sp),
                    ServiceControlModel.solped == None,
                    ServiceControlModel.solped == ''
                ))
            elif has_empty_sp:
                data_filter.append(or_(
                    ServiceControlModel.solped == None,
                    ServiceControlModel.solped == ''
                ))
            elif real_sp:
                data_filter.append(ServiceControlModel.solped.in_(real_sp))

        if filters.get("client_id"):
            data_filter.append(ServiceControlModel.client_id == int(filters["client_id"]))

        if filters.get("client_line_id"):
            data_filter.append(ServiceControlModel.client_line_id == int(filters["client_line_id"]))

        if filters.get("responsible_id"):
            data_filter.append(ServiceControlModel.responsible_id == int(filters["responsible_id"]))

        if filters.get("consecutive"):
            data_filter.append(ServiceControlModel.consecutive == int(filters["consecutive"]))

        if filters.get("oc") and len(filters["oc"]) > 0:
            oc_values = filters["oc"]
            has_empty = "__EMPTY__" in oc_values
            real_values = [v for v in oc_values if v != "__EMPTY__"]
            if has_empty and real_values:
                data_filter.append(or_(
                    ServiceControlModel.oc.in_(real_values),
                    ServiceControlModel.oc == None,
                    ServiceControlModel.oc == ''
                ))
            elif has_empty:
                data_filter.append(or_(
                    ServiceControlModel.oc == None,
                    ServiceControlModel.oc == ''
                ))
            elif real_values:
                data_filter.append(ServiceControlModel.oc.in_(real_values))

        if filters.get("factura"):
            try:
                data_filter.append(ServiceControlModel.invoice == int(filters["factura"]))
            except (ValueError, TypeError):
                pass

        # Filtro por rango de fecha de facturación
        if filters.get("invoice_date_start"):
            inv_start = datetime.strptime(filters["invoice_date_start"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date >= inv_start)

        if filters.get("invoice_date_end"):
            inv_end = datetime.strptime(filters["invoice_date_end"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date <= inv_end)

        hes_list = self.querys.get_unique_hes_list(data_filter=data_filter)
        return self.tools.output(200, "Ok.", hes_list)

    def get_solped_list(self, data: dict):
        filters = data.get("filters", {})
        data_filter = []

        if filters.get("start_date"):
            start = datetime.strptime(filters["start_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date >= start)

        if filters.get("end_date"):
            end = datetime.strptime(filters["end_date"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.activity_date <= end)

        if filters.get("service_status") and len(filters["service_status"]) > 0:
            data_filter.append(ServiceControlModel.service_status.in_(filters["service_status"]))

        if filters.get("report_status") and len(filters["report_status"]) > 0:
            data_filter.append(ServiceControlModel.report_status.in_(filters["report_status"]))

        if filters.get("client_id"):
            data_filter.append(ServiceControlModel.client_id == int(filters["client_id"]))

        if filters.get("client_line_id"):
            data_filter.append(ServiceControlModel.client_line_id == int(filters["client_line_id"]))

        if filters.get("responsible_id"):
            data_filter.append(ServiceControlModel.responsible_id == int(filters["responsible_id"]))

        if filters.get("consecutive"):
            data_filter.append(ServiceControlModel.consecutive == int(filters["consecutive"]))

        if filters.get("hes") and len(filters["hes"]) > 0:
            data_filter.append(ServiceControlModel.hes.in_(filters["hes"]))

        if filters.get("oc") and len(filters["oc"]) > 0:
            oc_values = filters["oc"]
            has_empty = "__EMPTY__" in oc_values
            real_values = [v for v in oc_values if v != "__EMPTY__"]
            if has_empty and real_values:
                data_filter.append(or_(
                    ServiceControlModel.oc.in_(real_values),
                    ServiceControlModel.oc == None,
                    ServiceControlModel.oc == ''
                ))
            elif has_empty:
                data_filter.append(or_(
                    ServiceControlModel.oc == None,
                    ServiceControlModel.oc == ''
                ))
            elif real_values:
                data_filter.append(ServiceControlModel.oc.in_(real_values))

        if filters.get("factura"):
            try:
                data_filter.append(ServiceControlModel.invoice == int(filters["factura"]))
            except (ValueError, TypeError):
                pass

        if filters.get("invoice_date_start"):
            inv_start = datetime.strptime(filters["invoice_date_start"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date >= inv_start)

        if filters.get("invoice_date_end"):
            inv_end = datetime.strptime(filters["invoice_date_end"], "%Y-%m-%d").date()
            data_filter.append(ServiceControlModel.invoice_date <= inv_end)

        solped_list = self.querys.get_unique_solped_list(data_filter=data_filter)
        return self.tools.output(200, "Ok.", solped_list)

    def update_inline_status(self, data: dict):
        try:
            record_id = data.get("record_id")
            if not record_id:
                raise CustomException("El campo record_id es requerido.")

            self.querys.check_param_exists(
                ServiceControlModel,
                record_id,
                "Control de servicio"
            )

            data_update = {}
            if "service_status" in data and data["service_status"] is not None:
                data_update["service_status"] = int(data["service_status"])
            if "report_status" in data and data["report_status"] is not None:
                data_update["report_status"] = int(data["report_status"])
            if "hes" in data:
                data_update["hes"] = data["hes"].strip() if data["hes"] else None

            if not data_update:
                raise CustomException("No se proporcionaron campos para actualizar.")

            self.querys.update_service_control(record_id, data_update)

            return self.tools.output(200, "Estado actualizado correctamente.")

        except CustomException as ex:
            raise ex
        except Exception as ex:
            raise CustomException(str(ex))

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

    def convert_multiple_to_report(self, data: dict):
        """Convierte masivamente varios controles de servicio en reportes."""
        record_ids = data.get("record_ids", [])
        if not record_ids:
            raise CustomException("Debe enviar al menos un registro para convertir.")

        converted = []
        errors = []

        for record_id in record_ids:
            try:
                sc = self.querys.get_service_control(record_id)
                if not sc:
                    errors.append({"id": record_id, "error": "No encontrado"})
                    continue
                if sc.report_id:
                    errors.append({"id": record_id, "error": f"Ya conertido (reporte #{sc.report_id})"})
                    continue

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
                self.querys.update_service_control(record_id, {
                    "report_id": new_report_id,
                    "consecutive": new_report_id,
                })
                converted.append({"sc_id": record_id, "report_id": new_report_id})

            except Exception as ex:
                errors.append({"id": record_id, "error": str(ex)})

        return self.tools.output(200, f"{len(converted)} reporte(s) creado(s) correctamente.", {
            "converted": converted,
            "errors": errors
        })

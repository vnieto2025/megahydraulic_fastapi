from decimal import Decimal
from Utils.tools import Tools, CustomException
from Models.type_service_model import TypeServiceModel
from Models.type_equipment_model import TypeEquipmentModel
from Models.components_model import ComponentsModel
from Models.service_status_model import ServiceStatusModel
from Models.report_status_model import ReportStatusModel
from Models.task_list_model import TaskListModel
from Models.task_list_by_equipment_model import TaskListEquipmentModel
from Models.equipment_tools_model import EquipmentToolsModel
from Models.service_activities_model import ServiceActivitiesModel
from Models.labor_type_model import LaborTypeModel

CATALOG_REGISTRY = {
    "type_service":      {"model": TypeServiceModel,      "fields": ["name"]},
    "type_equipment":     {"model": TypeEquipmentModel,    "fields": ["order", "name"]},
    "components":         {"model": ComponentsModel,       "fields": ["name"]},
    "service_status":     {"model": ServiceStatusModel,    "fields": ["name"]},
    "report_status":      {"model": ReportStatusModel,     "fields": ["name"]},
    "task_list":          {"model": TaskListModel,         "fields": ["name"]},
    "equipment_tools":    {"model": EquipmentToolsModel,   "fields": ["name", "unit", "unit_price"]},
    "service_activities": {"model": ServiceActivitiesModel, "fields": ["sap_code", "description", "unit_price"]},
    "labor_types":        {"model": LaborTypeModel,        "fields": ["code", "description", "unit", "value"]},
}


def _serialize(record, fields):
    row = {"id": record.id, "status": record.status}
    for field in fields:
        value = getattr(record, field)
        row[field] = float(value) if isinstance(value, Decimal) else value
    return row


class CatalogParams:

    def __init__(self, db):
        self.tools = Tools()
        self.db = db

    def _get_entity_config(self, entity: str):
        config = CATALOG_REGISTRY.get(entity)
        if not config:
            raise CustomException(f"Catálogo '{entity}' no reconocido.")
        return config

    def list_catalog(self, data: dict):
        entity = data.get("entity")
        config = self._get_entity_config(entity)
        model = config["model"]
        fields = config["fields"]

        records = self.db.query(model).order_by(model.id.desc()).all()
        response = [_serialize(r, fields) for r in records]

        return self.tools.output(200, "Ok.", response)

    def create_catalog(self, data: dict):
        entity = data.get("entity")
        config = self._get_entity_config(entity)
        model = config["model"]
        fields = config["fields"]
        values = data.get("data", {})

        try:
            record = model()
            for field in fields:
                if field in values:
                    setattr(record, field, values[field])
            record.status = 1
            self.db.add(record)
            self.db.commit()
        except Exception as ex:
            self.db.rollback()
            raise CustomException(str(ex))

        return self.tools.output(201, "Registro creado correctamente.", {"id": record.id})

    def update_catalog(self, data: dict):
        entity = data.get("entity")
        config = self._get_entity_config(entity)
        model = config["model"]
        fields = config["fields"]
        record_id = data.get("id")
        values = data.get("data", {})

        record = self.db.query(model).filter(model.id == record_id).first()
        if not record:
            raise CustomException("Registro no encontrado.")

        try:
            data_update = {field: values[field] for field in fields if field in values}
            if data_update:
                self.db.query(model).filter(model.id == record_id).update(data_update)
                self.db.commit()
        except Exception as ex:
            self.db.rollback()
            raise CustomException(str(ex))

        return self.tools.output(200, "Registro actualizado correctamente.")

    def toggle_status(self, data: dict):
        entity = data.get("entity")
        config = self._get_entity_config(entity)
        model = config["model"]
        record_id = data.get("id")
        status = data.get("status")

        record = self.db.query(model).filter(model.id == record_id).first()
        if not record:
            raise CustomException("Registro no encontrado.")

        try:
            self.db.query(model).filter(model.id == record_id).update({"status": status})
            self.db.commit()
        except Exception as ex:
            self.db.rollback()
            raise CustomException(str(ex))

        message = "Registro activado correctamente." if status == 1 else "Registro anulado correctamente."
        return self.tools.output(200, message)

    # ── Tareas por Equipo (relación N:M) ─────────────────────────────────────────
    def list_task_equipment(self, data: dict):
        equipment_id = data.get("equipment_id")
        if not equipment_id:
            raise CustomException("El equipo es requerido.")

        tasks = self.db.query(TaskListModel).filter(
            TaskListModel.status == 1
        ).order_by(TaskListModel.name.asc()).all()

        assigned_ids = {
            row.task_id for row in self.db.query(TaskListEquipmentModel).filter(
                TaskListEquipmentModel.equipment_id == equipment_id,
                TaskListEquipmentModel.status == 1
            ).all()
        }

        response = [
            {"id": t.id, "name": t.name, "assigned": t.id in assigned_ids}
            for t in tasks
        ]

        return self.tools.output(200, "Ok.", response)

    def toggle_task_equipment(self, data: dict):
        equipment_id = data.get("equipment_id")
        task_id = data.get("task_id")
        assign = data.get("assign")

        if not equipment_id or not task_id:
            raise CustomException("El equipo y la tarea son requeridos.")

        try:
            relation = self.db.query(TaskListEquipmentModel).filter(
                TaskListEquipmentModel.equipment_id == equipment_id,
                TaskListEquipmentModel.task_id == task_id
            ).first()

            if assign:
                if relation:
                    relation.status = 1
                else:
                    relation = TaskListEquipmentModel()
                    relation.equipment_id = equipment_id
                    relation.task_id = task_id
                    relation.status = 1
                    self.db.add(relation)
            else:
                if relation:
                    relation.status = 0

            self.db.commit()
        except Exception as ex:
            self.db.rollback()
            raise CustomException(str(ex))

        message = "Tarea asignada correctamente." if assign else "Tarea desasignada correctamente."
        return self.tools.output(200, message)

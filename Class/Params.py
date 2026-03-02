from Utils.tools import Tools
from Utils.querys import Querys

class Param:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)

    def get_type_document(self):

        type_documents = self.querys.get_type_document()
        return self.tools.output(200, "Ok.", type_documents)

    def get_type_user(self):

        type_users = self.querys.get_type_user()
        return self.tools.output(200, "Ok.", type_users)

    def get_type_maintenance(self):

        type_maintenance = self.querys.get_type_maintenance()
        return self.tools.output(200, "Ok.", type_maintenance)

    def get_type_service(self):

        type_service = self.querys.get_type_service()
        return self.tools.output(200, "Ok.", type_service)

    def get_type_equipments(self):

        type_equipments = self.querys.get_type_equipments()
        return self.tools.output(200, "Ok.", type_equipments)


    def get_tasks_by_equipment(self, data: dict):

        equipment = data["equipment"]
        tasks = self.querys.get_tasks_by_equipment(equipment)
        return self.tools.output(200, "Ok.", tasks)

    def get_lines_by_client(self, data: dict):

        client = data["client"]
        lines = self.querys.get_lines_by_client(client)
        return self.tools.output(200, "Ok.", lines)

    def get_users_by_client(self, data: dict):

        client = data["client"]
        lines = self.querys.get_users_by_client(client)
        return self.tools.output(200, "Ok.", lines)

    def get_clients(self):

        clients = self.querys.get_clients()
        return self.tools.output(200, "Ok.", clients)

    def get_service_statuses(self):

        service_statuses = self.querys.get_service_statuses()
        return self.tools.output(200, "Ok.", service_statuses)

    def get_report_statuses(self):

        report_statuses = self.querys.get_report_statuses()
        return self.tools.output(200, "Ok.", report_statuses)

    def get_components(self):

        components = self.querys.get_components()
        return self.tools.output(200, "Ok.", components)

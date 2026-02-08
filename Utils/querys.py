

from Utils.tools import Tools, CustomException
from Models.user_model import UserModel
from Models.type_document_model import TypeDocumentModel
from Models.user_type_model import TypeUserModel
from Models.report_type_service_model import ReportTypeServiceModel
from Models.type_service_model import TypeServiceModel
from Models.type_equipment_model import TypeEquipmentModel
from Models.task_list_model import TaskListModel
from Models.task_list_by_equipment_model import TaskListEquipmentModel
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from Models.client_user_model import ClientUserModel
from Models.report_model import ReportModel
from Models.report_details_model import ReportDetailsModel
from Models.report_files_model import ReportFilesModel
from Models.report_attach_files_model import ReportAttachFilesModel
from Models.module_model import ModulesModel
from Models.permission_model import PermissionModel
from sqlalchemy import func, and_

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

    # Query for obtain data of user to log
    def get_user(self, document: str):

        query = self.db.query(
            UserModel
        ).filter(
            UserModel.document == document, UserModel.status == 1,
        ).first()


        if not query:
            raise CustomException("User not found.")
        
        permission = list()
        query2 = self.db.query(
            ModulesModel.id,
            ModulesModel.name, 
            ModulesModel.description, 
            ModulesModel.icon,
            ModulesModel.action
        ).join(
            PermissionModel,
            PermissionModel.module_id == ModulesModel.id
        ).join(
            TypeUserModel,
            TypeUserModel.id == PermissionModel.type_user_id
        ).filter(
            ModulesModel.status == 1,
            PermissionModel.status == 1,
            TypeUserModel.status == 1,
            TypeUserModel.id == query.user_type_id
        ).order_by(
            PermissionModel.module_id.asc()
        ).all()

        if query2:
            for key in query2:
                permission.append({
                    "id": key.id,
                    "name": key.name,
                    "description": key.description,
                    "icon": key.icon,
                    "action": key.action,
                })
        
        result = {
            "id": query.id,
            "document": query.document,
            "first_name": str(query.first_name).capitalize(),
            "last_name": str(query.last_name).capitalize(),
            "user_type_id": query.user_type_id,
            "password": query.password,
            "email": query.email,
            "photo": query.photo,
            "permission": permission,
        }

        return result
    
    # Query for have all type documents
    def get_type_document(self):

        response = list()
                
        query = self.db.query(
            TypeDocumentModel
        ).filter(
            TypeDocumentModel.status == 1
        ).all()

        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name,
                "description": key.description
            })
        
        return response

    # Query for have all type users
    def get_type_user(self):

        response = list()
                
        query = self.db.query(
            TypeUserModel
        ).filter(
            TypeUserModel.status == 1
        ).all()

        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all type maintenances
    def get_clients(self):

        response = list()
                
        query = self.db.query(
            ClientModel
        ).filter(
            ClientModel.status == 1
        ).all()

        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all type services
    def get_type_service(self):

        response = list()
                
        query = self.db.query(
            TypeServiceModel
        ).filter(
            TypeServiceModel.status == 1
        ).all()

        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all type equipments
    def get_type_equipments(self):

        response = list()
                
        query = self.db.query(
            TypeEquipmentModel
        ).filter(
            TypeEquipmentModel.status == 1
        ).order_by(
            TypeEquipmentModel.order.asc()
        ).all()

        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all task by equipment
    def get_tasks_by_equipment(self, equipment: int):

        response = list()
                
        with self.db:
            query = self.db.query(
                TaskListModel.id, TaskListModel.name
            ).join(
                TaskListEquipmentModel, 
                TaskListModel.id == TaskListEquipmentModel.task_id,
                isouter=True
            ).join(
                TypeEquipmentModel, 
                TypeEquipmentModel.id == TaskListEquipmentModel.equipment_id,
                isouter=True
            ).filter(
                TypeEquipmentModel.status == 1,
                TaskListModel.status == 1,
                TaskListEquipmentModel.status == 1,
                TaskListEquipmentModel.equipment_id == equipment
            ).all()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all lines by client
    def get_lines_by_client(self, client: int):

        response = list()
                
        with self.db:
            query = self.db.query(
                ClientLinesModel.id, ClientLinesModel.name
            ).join(
                ClientModel, 
                ClientModel.id == ClientLinesModel.client_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientLinesModel.client_id == client
            ).all()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all users by client
    def get_users_by_client(self, client: int):

        response = list()
                
        with self.db:
            query = self.db.query(
                ClientUserModel.id, ClientUserModel.full_name
            ).join(
                ClientModel, 
                ClientModel.id == ClientUserModel.client_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientUserModel.status == 1,
                ClientUserModel.client_id == client
            ).all()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": str(key.full_name).upper()
            })
        
        return response

    # Function to verify if exists a field of any list of params
    def check_param_exists(self, model: any, param_to_find: int, field: str):

        query = self.db.query(
            model
        ).filter(
            model.id == param_to_find, model.status == 1
        ).first()


        msg = f"Field {field} doesn't exists."
        if not query:
            raise CustomException(msg)

        return query
    
    # Query for insert report.
    def create_report(self, data: dict):

        try:
            report = ReportModel(data)
            self.db.add(report)
            self.db.commit()
            report_id = report.id
            return report_id
        except Exception as ex:
            raise CustomException(str(ex))

    # Query for types maintenances.
    def insert_report_details(self, data: dict):
        try:
            details = ReportDetailsModel(data)
            self.db.add(details)
            self.db.commit()
    
        except Exception as ex:
            raise CustomException(str(ex))
        
        return True

    # Inserting data.
    def insert_data(self, model: any, data: dict):

        try:
            model_data = model(data)
            self.db.add(model_data)
            self.db.commit()
            model_id = model_data.id
            return model_id
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))

    # switching rows in 0 status.
    def deactive_data(self, model: any, report_id: dict):

        try:
            query = self.db.query(
                model
            ).filter(
                model.report_id == report_id, model.status == 1
            ).all()

            if not query:
                return True

            for key in query:
                key.status = 0
                self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for get the data for the report
    def get_data_report(self, report_id):

        try:

            response = dict()
                    
            query = self.db.query(
                ReportModel.id, 
                ReportModel.activity_date,
                ReportModel.client_id,
                ClientModel.name.label('client_name'),
                ReportModel.client_line_id,
                ClientLinesModel.name.label('client_line'),
                ReportModel.person_receives.label('person_receive_id'),
                ClientUserModel.full_name.label('person_receive_name'),
                ReportModel.om,
                ReportModel.solped,
                ReportModel.buy_order,
                ReportModel.position,
                ReportModel.equipment_type_id,
                TypeEquipmentModel.name.label('equipment_type_name'),
                ReportModel.equipment_name,
                ReportModel.service_description,
                ReportModel.information,
            ).join(
                ClientModel, 
                ClientModel.id == ReportModel.client_id,
                isouter=True
            ).join(
                ClientLinesModel, 
                ClientLinesModel.id == ReportModel.client_line_id,
                isouter=True
            ).join(
                ClientUserModel, 
                ClientUserModel.id == ReportModel.person_receives,
                isouter=True
            ).join(
                TypeEquipmentModel, 
                TypeEquipmentModel.id == ReportModel.equipment_type_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientUserModel.status == 1,
                TypeEquipmentModel.status == 1,
                ReportModel.id == report_id,
                ReportModel.status == 1
            ).first()
            
            if query:
                response = {
                    "id": query.id,
                    "activity_date": str(query.activity_date),
                    "client_id": query.client_id,
                    "client_name": query.client_name,
                    "client_line_id": query.client_line_id,
                    "client_line": query.client_line,
                    "person_receive_id": query.person_receive_id,
                    "person_receive_name": str(query.person_receive_name).upper(),
                    "om": query.om,
                    "solped": query.solped,
                    "buy_order": query.buy_order,
                    "position": query.position,
                    "information": query.information,
                    "equipment_type_id": query.equipment_type_id,
                    "equipment_type_name": query.equipment_type_name,
                    "equipment_name": str(query.equipment_name).upper(),
                    "service_description": str(query.service_description).capitalize(),
                }

                type_service = list()
                files = list()
                tasks = list()

                query2 = self.db.query(
                    ReportTypeServiceModel.report_id,
                    TypeServiceModel.id,
                    TypeServiceModel.name
                ).join(
                    TypeServiceModel, 
                    TypeServiceModel.id == ReportTypeServiceModel.type_service_id,
                    isouter=True
                ).filter(
                    ReportTypeServiceModel.report_id == report_id,
                    ReportTypeServiceModel.status == 1,
                    TypeServiceModel.status == 1
                ).all()

                if query2:
                    for key in query2:
                        type_service.append({
                            "id": key.id,
                            "report_id": key.report_id,
                            "name": key.name
                        })

                response.update({"type_service": type_service})

                query3 = self.db.query(
                    ReportFilesModel.id, ReportFilesModel.path,
                    ReportFilesModel.description
                ).filter(
                    ReportFilesModel.report_id == report_id,
                    ReportFilesModel.status == 1
                ).all()

                if query3:
                    for key in query3:
                        files.append({
                            "id": key.id,
                            "path": key.path,
                            "description": key.description
                        })

                response.update({"files": files})

                query4 = self.db.query(
                    ReportModel.id,
                    ReportDetailsModel.task_id,
                    TaskListModel.name,
                    ReportDetailsModel.positive,
                    ReportDetailsModel.negative,
                    ReportDetailsModel.description,
                ).join(
                    ReportDetailsModel,
                    ReportDetailsModel.report_id == ReportModel.id
                ).join(
                    TaskListModel,
                    TaskListModel.id == ReportDetailsModel.task_id
                ).filter(
                    ReportDetailsModel.status == 1,
                    TaskListModel.status == 1,
                    ReportModel.status == 1,
                    ReportDetailsModel.report_id == report_id
                ).all()

                if query4:
                    for key in query4:
                        tasks.append({
                            "id": key.task_id,
                            "name": key.name,
                            "positive": key.positive,
                            "negative": key.negative,
                            "description": str(key.description).capitalize(),
                        })

                response.update({"tasks": tasks})

        except Exception as ex:
            raise CustomException(str(ex))


        return response

    # Query for get the reports according to case
    def list_reports(self, data, user_id = None, state: bool = True, data_filter: list = []):
        
        try:
            response = list()
            query = self.db.query(
                ReportModel.id, 
                ReportModel.activity_date,
                ClientModel.name.label('client_name'),
                ClientLinesModel.name.label('client_line'),
                ClientUserModel.full_name.label('person_receive_name'),
                ReportModel.om,
                ReportModel.solped,
                ReportModel.buy_order,
                ReportModel.position,
                TypeEquipmentModel.name.label('type_equipment_name'),
                ReportModel.equipment_name,
                UserModel.first_name,
                UserModel.last_name
            ).join(
                ClientModel, 
                ClientModel.id == ReportModel.client_id,
                isouter=True
            ).join(
                ClientLinesModel, 
                ClientLinesModel.id == ReportModel.client_line_id,
                isouter=True
            ).join(
                ClientUserModel, 
                ClientUserModel.id == ReportModel.person_receives,
                isouter=True
            ).join(
                TypeEquipmentModel, 
                TypeEquipmentModel.id == ReportModel.equipment_type_id,
                isouter=True
            ).join(
                UserModel, 
                UserModel.id == ReportModel.user_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientUserModel.status == 1,
                TypeEquipmentModel.status == 1,
                ReportModel.type_report == 0,
                UserModel.status == 1,
                ReportModel.status == 1
            )

            if not state:
                query = query.filter(
                    ReportModel.user_id == user_id
                )

            if query:
                if data_filter: query = query.filter(and_(*data_filter))
                query = query.order_by(
                    ReportModel.id.desc()
                )
            
                reg_cont = query.count()

                reports = query.limit(data["limit"]).offset(data["limit"]*(int(data["position"])-1))

                response = {"reports": reports, "reg_cont": reg_cont}

            return response

        except Exception as ex:
            raise CustomException(str(ex))

    # Query for find images and update the description.
    def find_image_and_update(self, report_id, img):
        
        print(f"img: {img}")
        try:
            query = self.db.query(
                ReportFilesModel
            ).filter(
                ReportFilesModel.report_id == report_id,
                ReportFilesModel.path == img["img"],
            ).first()

            if query:
                query.description = img["description"]
                query.status = 1
                self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for update the information of report
    def edit_report(self, data):
        
        try:
            query = self.db.query(
                ReportModel
            ).filter(
                ReportModel.id == data["report_id"],
                ReportModel.status == 1
            ).first()

            if query:
                query.activity_date = data["activity_date"]
                query.client_id = data["client_id"]
                query.client_line_id = data["client_line_id"]
                query.person_receives = data["person_receives"]
                query.om = data["om"]
                query.solped = data["solped"]
                query.buy_order = data["buy_order"]
                query.position = data["position"]
                query.equipment_type_id = data["equipment_type_id"]
                query.equipment_name = data["equipment_name"]
                query.service_description = data["service_description"]
                query.information = data["information"]
                self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for obtain the data of user
    def get_data_user(self, user_id):

        result = dict()
        try:
            query = self.db.query(
                UserModel
            ).filter(
                UserModel.id == user_id, UserModel.status == 1,
            ).first()
    

            if query:
                result = {
                    "id": query.id,
                    "type_document": query.type_document,
                    "document": query.document,
                    "first_name": query.first_name,
                    "second_name": query.second_name,
                    "last_name": query.last_name,
                    "second_last_name": query.second_last_name,
                    "email": query.email
                }

            return result

        except Exception as ex:
            raise CustomException(str(ex))

    # Query for update user
    def update_user(self, data: dict):

        try:
            query = self.db.query(
                UserModel
            ).filter(
                UserModel.id == data["user_id"],
                UserModel.status == 1
            ).first()

            if query:
                full_name = f"{data["first_name"]} {data["second_name"]} {data["last_name"]} {data["second_last_name"]}"
                query.first_name = data["first_name"]
                query.second_name = data["second_name"]
                query.last_name = data["last_name"]
                query.second_last_name = data["second_last_name"]
                query.full_name = full_name
                query.email = data["email"]
                photo = data.get("photo", '')
                if photo:
                    query.photo = photo
                    
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return photo

    # Query for search if document exists.
    def check_document_exists(self, document):

        query = self.db.query(
            UserModel
        ).filter(
            UserModel.document == document,
            UserModel.status == 1
        ).first()


        msg = "Usuario ya se encuentra en la base de datos."
        if query:
            raise CustomException(msg)

        return query

    # Query for get the all the users
    def list_users(self, data):
        
        try:
            response = list()
            query = self.db.query(
                UserModel.id,
                UserModel.document,
                UserModel.first_name,
                UserModel.last_name,
                UserModel.email,
                UserModel.user_type_id,
                TypeUserModel.name.label('user_type'),
                UserModel.status,
            ).join(
                TypeUserModel, 
                TypeUserModel.id == UserModel.user_type_id,
                isouter=True
            ).filter(
                TypeUserModel.status == 1
            ).order_by(
                UserModel.id.asc()
            )

            if query:
                
                reg_cont = query.count()

                users = query.limit(data["limit"]).offset(data["limit"]*(int(data["position"])-1))

                for key in users:
                    first_name = str(key.first_name).upper()
                    last_name = str(key.last_name).upper()
                    response.append({
                        "id": key.id,
                        "document": key.document,
                        "user_name": f"{first_name} {last_name}",
                        "email": key.email,
                        "user_type_id": key.user_type_id,
                        "user_type": key.user_type,
                        "status": key.status,
                    })

                response = {"users": response, "reg_cont": reg_cont}

            return response

        except Exception as ex:
            raise CustomException(str(ex))

    # Query fot change status of the user
    def change_status(self, data: dict):

        try:
            query = self.db.query(
                UserModel
            ).filter(
                UserModel.id == data["user_id"]
            ).first()

            if query:
                query.status = data["status"]
                     
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for update type user id
    def update_type_user(self, data: dict):

        try:
            query = self.db.query(
                UserModel
            ).filter(
                UserModel.id == data["user_id"],
            ).first()

            if query:
                query.user_type_id = data["user_type_id"]
                     
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for update password
    def change_password(self, user_id: int, new_passwd: str):

        try:
            query = self.db.query(
                UserModel
            ).filter(
                UserModel.id == user_id,
                UserModel.status == 1,
            ).first()

            if query:
                query.password = new_passwd
                     
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for get the all the clients
    def list_clients(self, data):
        
        try:
            response = list()
            query = self.db.query(
                ClientModel.id,
                ClientModel.name,
                ClientModel.status,
            ).order_by(
                ClientModel.id.desc()
            )

            if query:
                
                reg_cont = query.count()

                clients = query.limit(data["limit"]).offset(data["limit"]*(int(data["position"])-1))

                for key in clients:
                    response.append({
                        "id": key.id,
                        "name": key.name,
                        "status": key.status,
                    })

                response = {"clients": response, "reg_cont": reg_cont}

            return response

        except Exception as ex:
            raise CustomException(str(ex))

    # Query for update data client
    def update_client(self, client_id: int, data_update: dict):

        try:
            query = self.db.query(
                ClientModel
            ).filter_by(
                id = client_id
            ).update(data_update)                     
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for get data client by id
    def get_client(self, client_id: int):

        try:
            response = dict()
            lines = list()
            persons = list()
            query = self.db.query(
                ClientModel.id,
                ClientModel.name
            ).filter(
                ClientModel.id == client_id, ClientModel.status == 1
            ).first()
            self.db.commit()

            if query:

                query2 = self.db.query(
                    ClientLinesModel.id,
                    ClientLinesModel.name
                ).filter(
                    ClientLinesModel.client_id == client_id,
                    ClientLinesModel.status == 1,
                ).all()

                if query2:
                    for key in query2:
                        lines.append({
                            "id": key.id,
                            "name": key.name,
                        })

                query3 = self.db.query(
                    ClientUserModel.id,
                    ClientUserModel.full_name,
                ).filter(
                    ClientUserModel.client_id == client_id,
                    ClientUserModel.status == 1,
                ).all()

                if query3:
                    for key in query3:
                        persons.append({
                            "id": key.id,
                            "name": key.full_name,
                        })

                response = {
                    "id": query.id,
                    "name": query.name,
                    "lines": lines,
                    "persons": persons,
                }

                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return response

    # Query for update client lines and person
    def update_lines_or_person(self, model: any, client_id: int, param_id: int, data_update: dict):

        try:
            query = self.db.query(
                model
            ).filter_by(
                id = param_id, client_id = client_id
            ).update(data_update)                     
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for change status of the report
    def change_status_report(self, report_id: int):

        try:
            self.db.query(
                ReportModel
            ).filter_by(
                id = report_id
            ).update({"status": 0})                     
            self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))

        
        return True

    # Query for get the data for the report
    def get_data_report_acesco(self, report_id):

        try:

            response = dict()
                    
            query = self.db.query(
                ReportModel.id, 
                ReportModel.activity_date,
                ReportModel.client_id,
                ClientModel.name.label('client_name'),
                ReportModel.client_line_id,
                ClientLinesModel.name.label('client_line'),
                ReportModel.person_receives.label('person_receive_id'),
                ClientUserModel.full_name.label('person_receive_name'),
                ReportModel.work_zone,
                ReportModel.om,
                ReportModel.solped,
                ReportModel.buy_order,
                ReportModel.position,
                ReportModel.service_description,
                ReportModel.information,
                ReportModel.service_value,
                ReportModel.conclutions,
                ReportModel.recommendations,
                ReportModel.tech_1,
                ReportModel.tech_2,
            ).join(
                ClientModel, 
                ClientModel.id == ReportModel.client_id,
                isouter=True
            ).join(
                ClientLinesModel, 
                ClientLinesModel.id == ReportModel.client_line_id,
                isouter=True
            ).join(
                ClientUserModel, 
                ClientUserModel.id == ReportModel.person_receives,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientUserModel.status == 1,
                ReportModel.id == report_id,
                ReportModel.status == 1
            ).first()

            # ✅ Convertir directamente en un diccionario
            response = query._asdict() if query else {}
            
            if response:
                files = list()
                anexos = list()

                query3 = self.db.query(
                    ReportFilesModel.id, ReportFilesModel.path,
                ).filter(
                    ReportFilesModel.report_id == report_id,
                    ReportFilesModel.status == 1
                ).all()

                if query3:
                    for key in query3:
                        files.append({
                            "id": key.id,
                            "path": key.path
                        })

                response.update({"files": files})

                query4 = self.db.query(
                    ReportAttachFilesModel.id, ReportAttachFilesModel.path,
                ).filter(
                    ReportAttachFilesModel.report_id == report_id,
                    ReportAttachFilesModel.status == 1
                ).all()

                if query4:
                    for key in query4:
                        anexos.append({
                            "id": key.id,
                            "path": key.path
                        })
                response.update({"anexos": anexos})

        except Exception as ex:
            raise CustomException(str(ex))


        return response

    # Query for get the reports according to case
    def list_reports_acesco(self, data, user_id = None, state: bool = True, data_filter: list = []):
        
        try:
            response = list()
            query = self.db.query(
                ReportModel.id, 
                ReportModel.activity_date,
                ClientModel.name.label('client_name'),
                ClientLinesModel.name.label('client_line'),
                ClientUserModel.full_name.label('person_receive_name'),
                ReportModel.work_zone,
                ReportModel.om,
                ReportModel.solped,
                ReportModel.buy_order,
                ReportModel.position,
                UserModel.first_name,
                UserModel.last_name
            ).join(
                ClientModel, 
                ClientModel.id == ReportModel.client_id,
                isouter=True
            ).join(
                ClientLinesModel, 
                ClientLinesModel.id == ReportModel.client_line_id,
                isouter=True
            ).join(
                ClientUserModel, 
                ClientUserModel.id == ReportModel.person_receives,
                isouter=True
            ).join(
                UserModel, 
                UserModel.id == ReportModel.user_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientUserModel.status == 1,
                ReportModel.type_report == 1,
                UserModel.status == 1,
                ReportModel.status == 1
            )

            if not state:
                query = query.filter(
                    ReportModel.user_id == user_id
                )

            if query:
                if data_filter: query = query.filter(and_(*data_filter))
                query = query.order_by(
                    ReportModel.id.desc()
                )
            
                reg_cont = query.count()

                reports = query.limit(data["limit"]).offset(data["limit"]*(int(data["position"])-1))

                response = {"reports": reports, "reg_cont": reg_cont}

            return response

        except Exception as ex:
            raise CustomException(str(ex))

    # Query for update the information of report
    def edit_report_acesco(self, data):
        
        try:
            query = self.db.query(
                ReportModel
            ).filter(
                ReportModel.id == data["report_id"],
                ReportModel.status == 1
            ).first()

            if query:
                query.activity_date = data["activity_date"]
                query.client_id = data["client_id"]
                query.client_line_id = data["client_line_id"]
                query.person_receives = data["person_receives"]
                query.work_zone = data["work_zone"]
                query.om = data["om"]
                query.solped = data["solped"]
                query.buy_order = data["buy_order"]
                query.position = data["position"]
                query.service_description = data["service_description"]
                query.information = data["information"]
                query.service_value = data["service_value"]
                query.conclutions = data["conclutions"]
                query.recommendations = data["recommendations"]
                query.tech_1 = data["tech_1"]
                query.tech_2 = data["tech_2"]
                self.db.commit()

            return True
                
        except Exception as ex:
            raise CustomException(str(ex))

    # Query for find images and update them.
    def find_image_and_update_version_two(self, model: any, report_id, img):
        
        try:
            query = self.db.query(
                model
            ).filter(
                model.report_id == report_id,
                model.path == img,
            ).first()

            if query:
                query.status = 1
                self.db.commit()
                
        except Exception as ex:
            raise CustomException(str(ex))
        
        return True

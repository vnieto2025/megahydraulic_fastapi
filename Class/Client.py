from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from Models.client_user_model import ClientUserModel

class Client:

    def __init__(self):
        self.tools = Tools()
        self.querys = Querys()

    # Function for create an user
    def create_client(self, data):

        client_name = data["client_name"]
        lines_list = data["lines_list"]
        person_list = data["person_list"]

        data_insert = {
            "name": client_name
        }
        client_id = self.querys.insert_data(ClientModel, data_insert)

        if lines_list:
            for line in lines_list:
                lines_insert = {"client_id": client_id, "name": line}
                self.querys.insert_data(ClientLinesModel, lines_insert)

        if person_list:
            for person in person_list:
                person_insert = {"client_id": client_id, "full_name": person}
                self.querys.insert_data(ClientUserModel, person_insert)


        return self.tools.output(201, "Cliente creado exitosamente.")

    # Function for list clients
    def list_client(self, data: dict):
        
        message = "Información de clientes generado correctamente."
        limit = int(data["limit"])
        page_position = int(data["position"])
        clients_dict = list()

        if page_position <= 0:
            message = "El campo posición no es válido"
            raise CustomException(message)
        
        clients = self.querys.list_clients(data)

        data_clients = clients["clients"]
        reg_cont = clients["reg_cont"]

        if not data_clients:
            message = "No hay listado de clientes que mostrar."
            return self.tools.output(200, message, data={
            "total_registros": 0,
            "total_pag": 0,
            "posicion_pag": 0,
            "clientes": []
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
            "clientes": []
        })

        clients_dict = {
            "total_registros": reg_cont,
            "total_pag": total_pag,
            "posicion_pag": page_position,
            "clientes": data_clients
        }

        return self.tools.output(200, message, clients_dict)

    # Function for update data client
    def update_client(self, data: dict):

        client_id = data["client_id"]

        if "status" in data:
            msg = "Usuario activado."
            if data["status"] == 0:
                msg = "Usuario desactivado."

            data_update = {"status": data["status"]}
            self.querys.update_client(client_id, data_update)
            return self.tools.output(200, msg)
        
        self.querys.check_param_exists(
            ClientModel,
            client_id,
            "cliente id"
        )

        client_name = data["client_name"]
        lines = data["lines_list"]
        persons = data["person_list"]

        data_update = {"name": client_name}
        self.querys.update_client(client_id, data_update)

        if lines:
            for line in lines:
                line_id = line["id"]
                data_update = {"name": line["name"]}      
                self.querys.update_lines_or_person(
                    ClientLinesModel,
                    client_id, 
                    line_id,
                    data_update
                )

        if persons:
            for person in persons:
                person_id = person["id"]
                data_update = {"full_name": person["name"]}      
                self.querys.update_lines_or_person(
                    ClientUserModel,
                    client_id, 
                    person_id,
                    data_update
                )

        return self.tools.output(200, "Cliente actualizado.")

    # Function for get client by id
    def get_client(self, data: dict):

        response = dict()
        client_id = data["client_id"]

        self.querys.check_param_exists(
            ClientModel,
            client_id,
            "cliente id"
        )

        response = self.querys.get_client(client_id)


        return self.tools.output(200, "Cliente encontrado.", response)

    # Function for add lines and person to existing client
    def add_line_person(self, data):

        client_id = data["client_id"]
        lines_list = data["lines_list"]
        person_list = data["person_list"]

        if lines_list:
            for line in lines_list:
                lines_insert = {"client_id": client_id, "name": line}
                self.querys.insert_data(ClientLinesModel, lines_insert)

        if person_list:
            for person in person_list:
                person_insert = {"client_id": client_id, "full_name": person}
                self.querys.insert_data(ClientUserModel, person_insert)


        return self.tools.output(201, "Parametros agregados exitosamente.")

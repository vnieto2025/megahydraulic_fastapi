from .validator import Validator


class Rules:
    """ Esta clase se encarga de validar los datos de entrada de la API
        y si hay un error, lanza una excepcion """

    val = Validator()

    def __init__(self, path: str, params: dict):
        path_dict = {
            "/login": self.__val_login,
            "/reports/create_report": self.__val_create_report,
            "/maintenance_types": self.__val_maintenance_types,
            "/service_types": self.__val_service_types,
            "/task_list": self.__val_task_list,
            "/params/get_tasks_by_equipment": self.__val_get_tasks_by_equipment,
            "/params/get_lines_by_client": self.__val_get_lines_by_client,
            "/params/get_users_by_client": self.__val_get_users_by_client,
            "/reports/generate_report": self.__val_generate_report,
            "/reports/list_report": self.__val_list_report,
            "/reports/edit_report": self.__val_edit_report,
            "/user/get_user": self.__val_get_user,
            "/user/create_user": self.__val_create_user,
            "/user/update_user": self.__val_update_user,
            "/user/change_status": self.__val_change_status,
            "/user/update_type_user": self.__val_update_type_user,
            "/client/create": self.__val_create_client,
            "/client/get_client": self.__val_get_client,
            "/client/add_line_person": self.__val_add_line_person,
        }
        # Se obtiene la funcion a ejecutar
        func = path_dict.get(path, None)
        if func:
            # Se ejecuta la funcion para obtener las reglas de validacion
            validacion_dict = func(params)

            # Se valida la datas
            self.val.validacion_datos_entrada(validacion_dict)
            
    # Validate data login
    def __val_login(self, params):
        validacion_dict = [
            {
                "tipo": "string",
                "campo": "documento",
                "valor": params["document"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "contraseña",
                "valor": params["password"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data create report
    def __val_create_report(self, params):
        validacion_dict = [
            {
                "tipo": "date",
                "campo": "fecha actividad",
                "valor": params["activity_date"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "cliente",
                "valor": params["client_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "línea del cliente",
                "valor": params["client_line_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "persona que recibe",
                "valor": params["person_receives"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "orden de mantenimiento",
                "valor": params["om"],
                "obligatorio": False,
            },
            {
                "tipo": "list",
                "campo": "tipos de servicio",
                "valor": params["type_service"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "tipo de equipo",
                "valor": params["equipment_type_id"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "nombre de equipo",
                "valor": params["equipment_name"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "descripción del servicio",
                "valor": params["service_description"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "información",
                "valor": params["information"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "lista de tareas",
                "valor": params["task_list"],
                "obligatorio": False,
            },
            {
                "tipo": "list",
                "campo": "archivos",
                "valor": params["files"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for types of maintenance
    def __val_maintenance_types(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "tipo mantenimiento",
                "valor": params,
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for types of services
    def __val_service_types(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "tipo servicio",
                "valor": params,
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for tasks list
    def __val_task_list(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "tarea id",
                "valor": params["task_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "positivo",
                "valor": params["positive"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "negativo",
                "valor": params["negative"],
                "obligatorio": False,
            },
            {
                "tipo": "string",
                "campo": "descripción de la lista de tarea",
                "valor": params["description"],
                "obligatorio": False,
            },
        ]
        return validacion_dict

    # Validate data for tasks by equipment
    def __val_get_tasks_by_equipment(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "tipo de equipo",
                "valor": params["equipment"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for lines by client
    def __val_get_lines_by_client(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "cliente",
                "valor": params["client"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for users by client
    def __val_get_users_by_client(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "cliente",
                "valor": params["client"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for generate report
    def __val_generate_report(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "reporte id",
                "valor": params["report_id"],
                "obligatorio": True,
            },
            {
                "tipo": "bool",
                "campo": "flag",
                "valor": params["flag"],
                "obligatorio": False,
            }
        ]
        return validacion_dict

    # Validate data list report
    def __val_list_report(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "limite",
                "valor": params["limit"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "posición de página",
                "valor": params["position"],
                "obligatorio": False,
            },
            {
                "tipo": "bool",
                "campo": "estado",
                "valor": params["state"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data create report
    def __val_edit_report(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "reporte id",
                "valor": params["report_id"],
                "obligatorio": True,
            },
            {
                "tipo": "date",
                "campo": "fecha actividad",
                "valor": params["activity_date"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "cliente",
                "valor": params["client_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "línea del cliente",
                "valor": params["client_line_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "persona que recibe",
                "valor": params["person_receives"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "orden de mantenimiento",
                "valor": params["om"],
                "obligatorio": False,
            },
            {
                "tipo": "list",
                "campo": "tipos de servicio",
                "valor": params["type_service"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "tipo de equipo",
                "valor": params["equipment_type_id"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "nombre de equipo",
                "valor": params["equipment_name"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "descripción del servicio",
                "valor": params["service_description"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "información",
                "valor": params["information"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "lista de tareas",
                "valor": params["task_list"],
                "obligatorio": False,
            },
            {
                "tipo": "list",
                "campo": "archivos",
                "valor": params["files"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for get data user
    def __val_get_user(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "usuario id",
                "valor": params["user_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data create user
    def __val_create_user(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "Tipo Documento",
                "valor": params["type_document"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Documento",
                "valor": params["document"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Primer Nombre",
                "valor": params["first_name"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Segundo Nombre",
                "valor": params["second_name"],
                "obligatorio": False,
            },
            {
                "tipo": "string",
                "campo": "Primer Apellido",
                "valor": params["last_name"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Segundo Apellido",
                "valor": params["second_last_name"],
                "obligatorio": False,
            },
            {
                "tipo": "email",
                "campo": "correo",
                "valor": params["email"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "tipo usuario",
                "valor": params["user_type_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data update user
    def __val_update_user(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "Usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Primer Nombre",
                "valor": params["first_name"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Segundo Nombre",
                "valor": params["second_name"],
                "obligatorio": False,
            },
            {
                "tipo": "string",
                "campo": "Primer Apellido",
                "valor": params["last_name"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Segundo Apellido",
                "valor": params["second_last_name"],
                "obligatorio": False,
            },
            {
                "tipo": "email",
                "campo": "correo",
                "valor": params["email"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "Foto",
                "valor": params["photo"],
                "obligatorio": False,
            }
        ]
        return validacion_dict

    # Validate data update user
    def __val_change_status(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "Usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "Estado",
                "valor": params["status"],
                "obligatorio": False,
            }
        ]
        return validacion_dict

    # Validate data update user type
    def __val_update_type_user(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "Usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            },
            {
                "tipo": "int",
                "campo": "Tipo Usuario",
                "valor": params["user_type_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for create client
    def __val_create_client(self, params):
        validacion_dict = [
            {
                "tipo": "string",
                "campo": "Nombre de cliente",
                "valor": params["client_name"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "Lista de líneas",
                "valor": params["lines_list"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "Lista de personas",
                "valor": params["person_list"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data for get client
    def __val_get_client(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "cliente id",
                "valor": params["client_id"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

# Validate data for create client
    def __val_add_line_person(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "cliente id",
                "valor": params["client_id"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "Lista de líneas",
                "valor": params["lines_list"],
                "obligatorio": False,
            },
            {
                "tipo": "list",
                "campo": "Lista de personas",
                "valor": params["person_list"],
                "obligatorio": False,
            }
        ]
        return validacion_dict

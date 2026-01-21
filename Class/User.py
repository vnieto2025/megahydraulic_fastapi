from werkzeug.security import check_password_hash, generate_password_hash
from Utils.tools import Tools, CustomException
from Utils.jwt_manager import create_token, validate_token
from Utils.querys import Querys
from Models.user_model import UserModel
from Models.type_document_model import TypeDocumentModel
from Models.user_type_model import TypeUserModel
import re
import base64
import uuid
import os
import hashlib
from datetime import datetime, timezone

ASSETS_FOLDER = "assets/img/"
PASSWD = "mega1234"

class User:

    def __init__(self, db):
        self.tools = Tools()
        self.querys = Querys(db)

    # Function for log to the app
    def login(self, data):

        document = data["document"]
        password = data["password"]

        data_user = self.querys.get_user(document)

        enc_passwd = data_user["password"]
        if not check_password_hash(enc_passwd, password):
            raise CustomException("Username or password incorrect.")

        token = create_token(
            {
                "document": document, 
                "user_type_id": data_user["user_type_id"]
            }
        )
        data_user["token"] = token
        data_user.pop("password")
        return self.tools.output(200, "Login successfully.", data_user)

    # Function for get user
    def get_user(self, data):
        
        user_id = data["user_id"]

        self.querys.check_param_exists(UserModel, user_id, "Usuario")

        data_user = self.querys.get_data_user(user_id)

        return self.tools.output(200, "Data found.", data_user)

    # Function for update an user
    def update_user(self, data: dict):

        user_id = data["user_id"]
        photo = data["photo"]

        data_user = self.querys.check_param_exists(UserModel, user_id, "Usuario")
        current_photo = data_user.photo

        if photo:
            img_path = self.proccess_images(photo)
            data["photo"] = img_path

            # Extraer solo el nombre del archivo de la foto actual
            current_photo_name = os.path.basename(current_photo)
            # Eliminar la foto actual si no es "no-profile.jpg"
            if current_photo_name != "no-profile.jpg":
                self.delete_image(current_photo)
        else:
            data.pop("photo")

        photo_url = self.querys.update_user(data)

        return self.tools.output(201, "Usuario actualizado.", photo_url)

    # Function for process image files base64 and save them
    def proccess_images(self, photo):
            
        try:
            # Extraer el formato de la imagen
            file_extension = self.extract_file_extension(photo)

            # Eliminar el prefijo base64 antes de decodificar
            base64_data = re.sub(r"^data:image/\w+;base64,", "", photo)

            # Decodificar la imagen base64
            file_data = base64.b64decode(base64_data)
        except Exception as e:
            raise CustomException(f"Error al decodificar la imagen {str(e)}")

        # Generar un nombre único para cada archivo
        file_name = f"{str(uuid.uuid4())}.{file_extension}"
        # file_path = os.path.join(ASSETS_FOLDER, file_name)
        file_path = f"{ASSETS_FOLDER}{file_name}"

        # Guardar la imagen decodificada en el servidor
        try:
            with open(file_path, "wb") as file:
                file.write(file_data)
        except Exception as e:
            raise CustomException(f"Error al guardar la imagen: {str(e)}")

        return file_path
    
    # Busca el prefijo que indica el tipo de archivo, como data:image/jpeg;base64,
    def extract_file_extension(self, file_base64: str):
        match = re.match(r"data:image/(?P<ext>\w+);base64,", file_base64)
        if not match:
            raise ValueError("Formato de imagen no válido o prefijo faltante")
        
        # Extrae la extensión (jpg, png, etc.)
        return match.group("ext")

    # Function for delete an image
    def delete_image(self, image_path):
        try:
            if os.path.exists(image_path):  # Verificar si el archivo existe
                os.remove(image_path)  # Eliminar el archivo
        except Exception as e:
            raise CustomException(f"Error al eliminar la imagen: {str(e)}")

    # Function for create an user
    def create_user(self, data):

        self.querys.check_document_exists(data["document"])
        self.querys.check_param_exists(
            TypeDocumentModel, 
            data["type_document"], 
            "Tipo Documento")
        
        passwd = self.hash_password(PASSWD)
        data["full_name"] = f"{data['first_name']} {data['second_name']} {data['last_name']} {data['second_last_name']}"
        data["password"] = passwd

        self.querys.insert_data(UserModel, data)

        return self.tools.output(201, "Usuario creado exitosamente.", PASSWD)

    # Function for hash a password
    def hash_password(self, passwd_str):

        try:
            # Genera el hash de la contraseña utilizando scrypt
            hashed_password = generate_password_hash(
                passwd_str, 
                method='scrypt', 
                salt_length=16
            )
            return hashed_password
        except Exception as ex:
            raise CustomException(str(ex))

    # Function for list users
    def list_user(self, data: dict):
        
        message = "Información de usuarios generado correctamente."
        limit = int(data["limit"])
        page_position = int(data["position"])
        users_dict = list()

        if page_position <= 0:
            message = "El campo posición no es válido"
            raise CustomException(message)
        
        users = self.querys.list_users(data)

        data_users = users["users"]
        reg_cont = users["reg_cont"]

        if not data_users:
            message = "No hay listado de usuarios que mostrar."
            return self.tools.output(200, message, data={
            "total_registros": 0,
            "total_pag": 0,
            "posicion_pag": 0,
            "usuarios": []
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
            "usuarios": []
        })

        users_dict = {
            "total_registros": reg_cont,
            "total_pag": total_pag,
            "posicion_pag": page_position,
            "usuarios": data_users
        }

        return self.tools.output(200, message, users_dict)

    # Function for change status 1 or 0
    def change_status(self, data: dict):
        
        msg = "Usuario activado."
        if data["status"] == 0:
            msg = "Usuario desactivado."

        self.querys.change_status(data)

        return self.tools.output(200, msg)

    # Function for update the type user
    def update_type_user(self, data: dict):

        self.querys.check_param_exists(
            TypeUserModel, 
            data["user_type_id"], 
            "Tipo Usuario"
        )

        self.querys.update_type_user(data)

        return self.tools.output(200, "Gestión actualizada.")

    # Function for change password
    def change_password(self, data: dict):
        
        user_id = data["user_id"]
        current_password = data["current_password"]
        new_password = data["new_password"]

        if current_password == new_password:
            raise CustomException("Ya está usando esa contraseña.")

        data_user = self.querys.check_param_exists(
            UserModel, 
            user_id, 
            "Usuario"
        )

        if not check_password_hash(data_user.password, current_password):
            raise CustomException("Contraseña actual incorrecta.")
        
        if len(new_password) < 8:
            raise CustomException("Contraseña debe tener mínimo 8 dígitos.")
        
        new_passwd = self.hash_password(new_password)

        self.querys.change_password(user_id, new_passwd)

        return self.tools.output(200, "Contraseña actualizada.")

    # Function for check token expiration time
    def check_token(self, token: str):
        """
        Verifica el tiempo restante del token JWT.
        Retorna los minutos restantes antes de que expire.
        """
        try:
            # Validar y decodificar el token
            payload = validate_token(token)
            
            # Obtener el tiempo de expiración del token
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                raise CustomException("Token inválido")
            
            # Calcular el tiempo restante en minutos
            now = datetime.now(timezone.utc)
            expiration_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            time_remaining = expiration_time - now
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            
            return self.tools.output(200, "Token verificado", {
                "minutes_remaining": minutes_remaining,
                "expiration_time": expiration_time.isoformat(),
                "is_about_to_expire": minutes_remaining <= 5
            })
            
        except CustomException as ce:
            raise ce
        except Exception as e:
            raise CustomException(f"Error al verificar token: {str(e)}")

# from fastapi.security import HTTPBearer
# from fastapi import Request, HTTPException
# from Utils.jwt_manager import validate_token
# from Utils.querys import Querys

# class JWTBearer(HTTPBearer):
#     async def __call__(self, request: Request):
#         auth = await super().__call__(request)
#         data = validate_token(auth.credentials)
#         data_user = Querys().get_user(data["document"])
#         if data["document"] != data_user["document"]:
#             raise HTTPException(status_code=400, detail="Credenciales invalidas")


from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException
from Utils.jwt_manager import validate_token

class JWTBearer(HTTPBearer):
    def __init__(self, required_roles: list = None):
        super(JWTBearer, self).__init__()
        self.required_roles = required_roles  # Lista de IDs de roles permitidos

    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        token_data = validate_token(auth.credentials)

        # Extrae el user_type_id del token
        user_type_id = token_data.get("user_type_id", None)

        # Verificar que el token tiene el documento esperado
        if "document" not in token_data:
            raise HTTPException(status_code=400, detail="Credenciales inválidas.")

        if user_type_id is None:
            raise HTTPException(status_code=403, detail="No role information found in token.")

        # Si hay roles requeridos, verifica que el user_type_id sea uno de ellos
        if self.required_roles and user_type_id not in self.required_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos suficientes para acceder a este recurso.")

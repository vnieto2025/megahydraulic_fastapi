from pydantic import BaseModel

class User(BaseModel):
    document: str
    password: str

from pydantic import BaseModel

class ClientCreate(BaseModel):
    phone_number: str
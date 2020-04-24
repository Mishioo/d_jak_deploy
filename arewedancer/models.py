from pydantic import BaseModel


class Patient(BaseModel):
    name: str
    surname: str

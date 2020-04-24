from pydantic import BaseModel


class Patient(BaseModel):
    name: str
    surname: str


class PatientResponse(BaseModel):
    id: int
    patient: Patient

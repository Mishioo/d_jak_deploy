from pydantic import BaseModel


class Patient(BaseModel):
    name: str
    surename: str  # misspell specified in requirements


class PatientResponse(BaseModel):
    id: int
    patient: Patient

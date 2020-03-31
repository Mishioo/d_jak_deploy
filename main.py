from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
app.patient_counter = 0
app.patients = {}


class Message(BaseModel):
    message: str


class MethodGetter(BaseModel):
    method: str


class Patient(BaseModel):
    name: str
    surname: str


class PatientResponse(BaseModel):
    id: int
    patient: dict


@app.get("/")
def root():
    return Message(message="Hello World during the coronavirus pandemic!")


@app.get("/method", response_model=MethodGetter)
def method_get():
    return MethodGetter(method='GET')


@app.post("/method", response_model=MethodGetter)
def method_post():
    return MethodGetter(method='POST')


@app.put("/method", response_model=MethodGetter)
def method_put():
    return MethodGetter(method='PUT')


@app.delete("/method", response_model=MethodGetter)
def method_delete():
    return MethodGetter(method='DELETE')


@app.post('/patient', response_model=PatientResponse)
def new_patient(patient: Patient):
    response = PatientResponse(id=app.patient_counter, patient=patient.dict())
    app.patients[app.patient_counter] = patient.dict()
    app.patient_counter += 1
    return response


@app.get("/hello/{name}", response_model=Message)
def hello_name(name: str):
    return Message(message=f"Hello {name}")

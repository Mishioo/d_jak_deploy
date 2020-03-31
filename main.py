from fastapi import FastAPI
from fastapi.responses import JSONResponse
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
    surename: str  # misspell specified in requirements


class PatientResponse(BaseModel):
    id: int
    patient: Patient


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


@app.get(
    '/patient/{pk}', response_model=Patient, responses={204: {}}
 )
def patient_get(pk: int):
    try:
        patient = app.patients[pk]
        return Patient(**patient)
    except KeyError:
        return JSONResponse(status_code=204, content={})


@app.get("/hello/{name}", response_model=Message)
def hello_name(name: str):
    return Message(message=f"Hello {name}")

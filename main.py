import base64

from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()
app.patient_counter = 0
app.patients = {}


class Patient(BaseModel):
    name: str
    surename: str  # misspell specified in requirements


class PatientResponse(BaseModel):
    id: int
    patient: Patient


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get("/welcome")
def welcome():
    return {"message": "Welcome to arewedancer!"}


@app.get("/method")
@app.post("/method")
@app.put("/method")
@app.delete("/method")
def method(request: Request):
    return {"method": request.method}


@app.post("/patient", response_model=PatientResponse)
def new_patient(patient: Patient):
    response = PatientResponse(id=app.patient_counter, patient=patient.dict())
    app.patients[app.patient_counter] = patient.dict()
    app.patient_counter += 1
    return response


@app.get("/patient/{pk}", response_model=Patient, responses={204: {}})
def patient_get(pk: int):
    try:
        patient = app.patients[pk]
        return Patient(**patient)
    except KeyError:
        return JSONResponse(status_code=204, content={})


@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello {name}"}


def decode_basic_auth(auth):
    encoded = bytes(auth[6:], "ascii")
    decoded = base64.b64decode(encoded).decode("utf-8")
    u, p = decoded.split(":")
    return {"username": u, "password": p}


@app.post("/login")
def login(authorization: str = Header(None)):
    auth = decode_basic_auth(authorization)
    return "{username} authorized with {password}".format(**auth)

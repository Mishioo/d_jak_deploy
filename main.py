import hashlib

from fastapi import FastAPI, Request, Cookie, Depends, HTTPException
from fastapi.responses import Response, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from starlette import status

app = FastAPI()
app.patient_counter = 0
app.patients = {}
app.users = {"trudnY": "PaC13Nt"}
app.sessions = {}

security = HTTPBasic()
SECRET_KEY = "Sphinx of black quartz, judge my vow."


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


def authorize(session_token: str = Cookie(None)):
    print(session_token)
    if not session_token or (session_token not in app.sessions):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login to get access to this resource.",
        )
    return True


@app.post("/patient", response_model=PatientResponse, dependencies=[Depends(authorize)])
def new_patient(patient: Patient):
    response = PatientResponse(id=app.patient_counter, patient=patient.dict())
    app.patients[app.patient_counter] = patient.dict()
    app.patient_counter += 1
    return response


@app.get(
    "/patient/{pk}",
    response_model=Patient,
    responses={204: {}},
    dependencies=[Depends(authorize)],
)
def patient_get(pk: int):
    try:
        patient = app.patients[pk]
        return Patient(**patient)
    except KeyError:
        return JSONResponse(status_code=204, content={})


@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello {name}"}


def create_token(username: str, password: str) -> str:
    token = hashlib.sha256(bytes(f"{username}{password}{SECRET_KEY}", "utf-8"))
    token = token.hexdigest()
    return token


def authenticate(username: str, password: str) -> str:
    if username not in app.users or not password == app.users[username]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or password"
        )
    token = create_token(username, password)
    app.sessions[token] = username
    return token


@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    session_token = authenticate(credentials.username, credentials.password)
    response = RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=session_token)
    return response


@app.get("/login")
def login_get(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    session_token = authenticate(credentials.username, credentials.password)
    response.set_cookie(key="session_token", value=session_token)
    return {"username": credentials.username, "token": session_token}


@app.post("/logout", dependencies=[Depends(authorize)])
def logout(session_token: str = Cookie(None)):
    print("in logout")
    del app.sessions[session_token]
    return RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)


@app.get("/test")
def test_cookie(session_token: str = Cookie(None)):
    if session_token:
        return {"user": app.sessions[session_token], "token": session_token}
    else:
        return {"user": "NO USER", "token": "NO SESSION"}

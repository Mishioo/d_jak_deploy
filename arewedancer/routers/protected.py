from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from .security import current_user
from ..models import Patient, PatientResponse

router = APIRouter()
router.patient_counter = 0
router.patients = {}

templates = Jinja2Templates(directory="templates")


@router.post("/patient", response_model=PatientResponse)
def new_patient(patient: Patient):
    router.patients[router.patient_counter] = patient.dict()
    router.patient_counter += 1
    return RedirectResponse(
        url=f"/patient/{router.patient_counter - 1}",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/patient/{pk}", response_model=Patient, responses={204: {}})
def patient_get(pk: int):
    try:
        patient = router.patients[pk]
        return Patient(**patient)
    except KeyError:
        return JSONResponse(status_code=204, content={})


@router.get("/welcome")
def welcome(request: Request, user: Optional[str] = Depends(current_user)):
    return templates.TemplateResponse(
        "welcome.html", {"request": request, "user": user}
    )

from typing import Dict, Optional
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from .security import current_user
from ..models import Patient


router = APIRouter()
router.patients = {}
templates = Jinja2Templates(directory="arewedancer/templates")


@router.get("/welcome")
def welcome(request: Request, user: Optional[str] = Depends(current_user)):
    return templates.TemplateResponse(
        "welcome.html", {"request": request, "user": user}
    )


@router.post("/patient")
def new_patient(patient: Patient):
    identifier = uuid.uuid4().hex
    router.patients[identifier] = patient.dict()
    return RedirectResponse(
        url=f"/patient/{identifier}",
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/patient", response_model=Dict[str, Patient])
def all_patients():
    return router.patients


@router.get("/patient/{pk}", response_model=Patient)
def patient_get(pk: str):
    try:
        patient = router.patients[pk]
        return Patient(**patient)
    except KeyError:
        return JSONResponse(status_code=204, content={})


@router.delete("/patient/{pk}", status_code=204)
def patient_delete(pk: str):
    try:
        del router.patients[pk]
    except KeyError:
        pass

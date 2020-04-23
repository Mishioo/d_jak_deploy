from fastapi import APIRouter
from fastapi.requests import Request

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@router.get("/method")
@router.post("/method")
@router.put("/method")
@router.delete("/method")
def method(request: Request):
    return {"method": request.method}


@router.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello {name}"}

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Message(BaseModel):
    message: str


class MethodGetter(BaseModel):
    method: str


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


@app.get("/hello/{name}", response_model=Message)
def hello_name(name: str):
    return Message(message=f"Hello {name}")

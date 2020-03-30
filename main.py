from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class HelloNameBase(BaseModel):
    message: str


@app.get("/")
def root():
    return HelloNameBase(message="Hello World during the coronavirus pandemic!")


@app.get("/hello/{name}", response_model=HelloNameBase)
def hello_name(name: str):
    return HelloNameBase(message=f"Hello {name}")

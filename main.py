from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


class HelloNameBase(BaseModel):
    message: str


@app.get("/hello/{name}", response_model=HelloNameBase)
def hello_name(name: str):
    return HelloNameBase(message=f"Hello {name}")

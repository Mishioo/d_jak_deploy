from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from .routers import security, protected, public
from .routers.security import authorize, current_user


templates = Jinja2Templates(directory="arewedancer/templates")

app = FastAPI()

app.include_router(security.router)
app.include_router(public.router)
app.include_router(protected.router, dependencies=[Depends(authorize)])


@app.get("/welcome", dependencies=[Depends(authorize)])
def welcome(request: Request, user: Optional[str] = Depends(current_user)):
    return templates.TemplateResponse(
        "welcome.html", {"request": request, "user": user}
    )

from fastapi import FastAPI, Depends

from .routers import security, protected, public
from .routers.security import authorize


app = FastAPI()

app.include_router(security.router)
app.include_router(public.router)
app.include_router(protected.router, dependencies=[Depends(authorize)])



import hashlib
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import Response, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette import status


router = APIRouter()
router.users = {"trudnY": "PaC13Nt"}
router.sessions = {}

security = HTTPBasic()
SECRET_KEY = "Sphinx of black quartz, judge my vow."


def authorize(session_token: str = Cookie(None)):
    print(session_token)
    if not session_token or (session_token not in router.sessions):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login to get access to this resource.",
        )
    return True


def create_token(username: str, password: str) -> str:
    token = hashlib.sha256(bytes(f"{username}{password}{SECRET_KEY}", "utf-8"))
    token = token.hexdigest()
    return token


def current_user(session_token: str = Cookie(None)) -> Optional[str]:
    try:
        return router.sessions[session_token]
    except KeyError:
        return None


def authenticate(username: str, password: str) -> str:
    if username not in router.users or not password == router.users[username]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or password"
        )
    token = create_token(username, password)
    router.sessions[token] = username
    return token


@router.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    session_token = authenticate(credentials.username, credentials.password)
    response = RedirectResponse(url="/welcome", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=session_token)
    return response


@router.get("/login")
def login_get(
    response: Response, credentials: HTTPBasicCredentials = Depends(security)
):
    session_token = authenticate(credentials.username, credentials.password)
    response.set_cookie(key="session_token", value=session_token)
    return {"username": credentials.username, "token": session_token}


@router.post("/logout", dependencies=[Depends(authorize)])
def logout(session_token: str = Cookie(None)):
    print("in logout")
    del router.sessions[session_token]
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

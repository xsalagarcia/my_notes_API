from typing import Annotated

from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import JSONResponse, Response

from app.router import service_errors_handler
from app.service import auth as service
from app.settings.settings import settings

router = APIRouter(prefix="/auth")


@router.post("/login")
@service_errors_handler
def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    jr = JSONResponse("Login ok")
    cookie = service.set_admin_session(username=username, password=password)
    jr.set_cookie(key="admin_session", value=cookie, max_age=settings.app_settings.admin_session_ttl_minutes * 60,
                  samesite="strict", httponly=True)
    return jr


@router.get("/logout")
@service_errors_handler
def logout(cookie: str = Depends(service.check_admin_session)):
    service.del_admin_session(cookie=cookie)
    jr = JSONResponse("Logged out")

    jr.delete_cookie(key="admin_session")
    return jr

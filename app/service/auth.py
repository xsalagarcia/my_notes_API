from typing import Annotated

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import APIKeyCookie

from app.exceptions.service import ServiceError
from app.settings.settings import settings
from app.data import cache

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
cookie_admin_session_scheme = APIKeyCookie(name="admin_session")
cookie_admin_session_scheme_no_error = APIKeyCookie(name="admin_session", auto_error=False)


def set_admin_session(username: str, password: str) -> str:
    """
    If username and password matches cookie value for session and sets it to the cache. Otherwise, raises ServiceError
    with 403.
    :param username:
    :param password:
    :return:
    """
    if not pwd_context.verify(password, settings.admin_key) or settings.admin_name != username:
        raise ServiceError(msg="Wrong username or password", suggested_http_code=403)
    else:
        return cache.set_admin_session()


def check_admin_session(cookie: Annotated[str, Depends(cookie_admin_session_scheme)]) -> str:
    """
    HTTPException with 403 if there is no cookie or there is no cache. Otherwise, returns the cookie content.
    :param cookie:
    :return:
    """
    in_cache = cache.get_admin_session()
    if in_cache is None or in_cache != cookie:
        raise HTTPException(detail="Not authenticated", status_code=403)
    return in_cache


def is_admin_logged(cookie: Annotated[str, Depends(cookie_admin_session_scheme_no_error)]) -> bool:
    """
    Returns true if admin is logged, otherwise false.
    :param cookie:
    :return:
    """
    in_cache = cache.get_admin_session()
    return in_cache is not None and in_cache == cookie


def del_admin_session():
    cache.del_admin_session()

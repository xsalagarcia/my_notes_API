from functools import wraps

from fastapi import HTTPException

from app.exceptions.service import ServiceError


def service_errors_handler(router_func):
    """
        Puts wrapped function into try block for ServiceError exceptions. If occurs, an HTTPException is raised
        try:
            code on wrapped function
        except ServiceError as e:
            if e.redirection is None:
                raise HTTPException(detail=e.msg, status_code=e.suggested_http_code)
            else:
                raise HTTPException(detail=e.msg,
                                    status_code=e.suggested_http_code,
                                    headers={"Location": e.redirection})
    """

    @wraps(router_func)
    def wrapper(*args, **kwargs):
        try:
            return router_func(*args, **kwargs)
        except ServiceError as e:
            if e.redirection is None:
                raise HTTPException(detail=e.msg, status_code=e.suggested_http_code)
            else:
                raise HTTPException(detail=e.msg,
                                    status_code=e.suggested_http_code,
                                    headers={"Location": e.redirection})

    return wrapper
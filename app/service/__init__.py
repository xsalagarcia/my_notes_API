from functools import wraps

from app.exceptions.database import DatabaseError
from app.exceptions.service import ServiceError


def data_errors_handler(router_func):
    """
        Puts wrapped function into try block for DatabaseError exceptions. If occurs, a ServiceError is raised

    """

    @wraps(router_func)
    def wrapper(*args, **kwargs):
        try:
            return router_func(*args, **kwargs)
        except DatabaseError as e:
            raise ServiceError(msg=e.msg, suggested_http_code=e.suggested_http_code, redirection=e.redirection)
    return wrapper
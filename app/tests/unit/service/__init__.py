from functools import wraps

from app.exceptions.database import DatabaseError
from app.exceptions.service import ServiceError


def data_errors_handler(service_func):
    """
        Puts wrapped function into try block for DatabaseError exceptions. If occurs, a ServiceError is raised
        using same message and suggested http code. For service layer.
        try:
            code on wrapped function
        except DatabaseError as e:
            raise ServiceError(msg=e.msg, suggested_http_code=e.suggested_http_code)
    """
    @wraps(service_func)
    def wrapper(*args, **kwargs):
        try:
            return service_func(*args, **kwargs)
        except DatabaseError as e:
            raise ServiceError(msg=e.msg, suggested_http_code=e.suggested_http_code)

    return wrapper

from app.data import redis_data
import secrets

from app.models.middleware import IpInSurveillance
from app.settings.settings import settings


def set_admin_session(ttl_seconds: None | int = None) -> str:
    """
    Sets cache admin session token and returns it. Default ttl is extracted from settings.
    :param ttl_seconds:
    :return: a token
    """
    admin_session_token = secrets.token_urlsafe(32)
    redis_data.set(name="admin_session", value=admin_session_token,
                   ex=ttl_seconds if ttl_seconds is not None else settings.app_settings.admin_session_ttl_minutes * 60)
    return admin_session_token


def get_admin_session() -> str | None:
    """
    :return: None if there is no associated cache. Otherwise, the associated token session.
    """
    return redis_data.get(name="admin_session")


def del_admin_session():
    redis_data.delete("admin_session")


def get_ip_in_surveillance(ip: str) -> IpInSurveillance | None:
    content = redis_data.hgetall(ip)
    if len(content) == 0:
        return None

    return IpInSurveillance(ip=ip, **content)


def create_or_update_ip_in_surveillance(ip_in_surveillance: IpInSurveillance):
    redis_data.hset(ip_in_surveillance.ip, mapping=ip_in_surveillance.model_dump(exclude={"ip"}))
    redis_data.expire(ip_in_surveillance.ip, settings.middleware_settings.ip_blocked_expires_minutes * 60)


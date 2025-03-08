import time

from app.data import cache
from app.models.middleware import IpInSurveillance
from app.settings.settings import settings


def is_ip_locked(ip: str) -> bool:
    """
    Returns True when ip is in surveillance at failed attempts are greather than... Otherwise, returns False
    :param ip:
    :return:
    """
    ip_in_surveillance = cache.get_ip_in_surveillance(ip=ip)
    if ip_in_surveillance is None or ip_in_surveillance.attempts < settings.middleware_settings.max_ip_fail_logins:
        return False
    return True


def add_login_fail(ip: str):
    ip_in_surveillance = cache.get_ip_in_surveillance(ip=ip)

    if ip_in_surveillance is None:
        ip_in_surveillance = IpInSurveillance(ip=ip)
    else:
        ip_in_surveillance.attempts += 1
        ip_in_surveillance.last_modification_timestamp = time.time()
    cache.create_or_update_ip_in_surveillance(ip_in_surveillance=ip_in_surveillance)
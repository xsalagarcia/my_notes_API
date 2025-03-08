class ServiceError(Exception):
    def __init__(self, msg: str, suggested_http_code: int = 401, redirection: str | None = None):
        """
        :param msg:
        :param suggested_http_code:
        :param redirection: Optional parameter for redirection management.
        """
        self.msg = msg
        self.suggested_http_code = suggested_http_code
        self.redirection = redirection


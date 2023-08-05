class BaseExceptionError(Exception):
    """
    Base Exception class for v2 APIs.
    All custom exceptions are created by extending this class.
    Exception has 4 attributes corresponding to details sent in 'error' object
    in response JSON -
        status - http status code
        code - application specific error code
        title - title of error
        detail - details of error
    """

    def __init__(self, status, code, title, detail):
        Exception.__init__(self)
        self.title = title
        self.detail = detail

    def as_dict(self):
        return {"title": self.title, "detail": self.detail}

    def as_str(self):
        exception_str = "Exception Type : " + self.__class__.__name__
        exception_str += "\nTitle - " + self.title if self.title else ""
        exception_str += "\nDetails - " + self.detail if self.detail else ""
        return exception_str

    def __str__(self):
        return f"{self.__class__.__name__} ({self.title}): {self.detail}"


class RequestException(Exception):
    def __init__(self, title, detail=None):
        self.title = title
        self.detail = detail


class UnauthorizedException(Exception):
    def __str__(self):
        return "Expired or Invalid Token"


class invalidApiResponseException(BaseExceptionError):
    def __init__(self, title=None, detail=None):
        if title:
            self.title = title
        if detail:
            self.detail = detail


def has_error_message(response):
    try:
        for key in response.json().keys():
            if key in {"error", "errors"}:
                return True
        return False
    except Exception:
        return False


def extract_json_api_error(response):
    error = response.json().get("error")
    if error is None:
        error = response.json().get("errors")[0]
    if "title" in error:
        title = error.get("title")
    if "detail" in error:
        detail = error.get("detail")
    return title, detail


def error_handler(response):
    if has_error_message(response):
        title, detail = extract_json_api_error(response)
        raise RequestException(title, detail)
    elif response.status_code == 401:
        raise UnauthorizedException

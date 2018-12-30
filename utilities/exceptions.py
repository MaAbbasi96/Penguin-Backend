from rest_framework.exceptions import APIException


class APIExceptionWithMetadata(APIException):
    def __init__(self, status_code, code, detail, metadata=None):
        super(APIExceptionWithMetadata, self).__init__(code=code, detail=detail)
        self.status_code = status_code
        self.metadata = metadata


class BusinessLogicException(Exception):
    """
    Is raised when some functionality does not conform to business rules.
    Leads to 409 error if caused from a call from http handlers
    """

    def __init__(self, code, detail):
        self.code = code
        self.detail = detail

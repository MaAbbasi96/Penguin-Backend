from rest_framework.exceptions import APIException


class APIExceptionWithMetadata(APIException):
    def __init__(self, status_code, code, detail, metadata=None):
        super(APIExceptionWithMetadata, self).__init__(code=code, detail=detail)
        self.status_code = status_code
        self.metadata = metadata
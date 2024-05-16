from fastapi import HTTPException as FastApiHTTPException


class HTTPException(FastApiHTTPException):
    def __init__(self, status_code, description=None):
        self.code = status_code
        super(HTTPException, self).__init__(status_code=status_code, detail=description)

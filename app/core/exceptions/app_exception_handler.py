from fastapi import status
from fastapi.responses import JSONResponse


def exception_message(error: str, message: str, internal_code: int = None):
    """
    Exception message returned by the application when an error occurs
    :param error: the type error type
    :param message: the error message
    :param internal_code: the error code
    """
    return {
        "error": error,
        "error_message": message,
        "internal_code": internal_code,
    }


def http_exception_handler(exc):
    """
    handle http exceptions raised by the application
    :param exc: the exception
    """
    return JSONResponse(
        content=exception_message(
            error="HttpException", message=exc.detail, internal_code=exc.status_code
        ),
        status_code=exc.status_code,
        media_type="application/json",
    )


def db_exception_handler(exc):
    """
    handle database exceptions raised by the application
    :param exc: the exception
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exception_message(
            error="DatabaseException",
            message=exc.orig.pgerror,
            internal_code=status.HTTP_400_BAD_REQUEST,
        ),
        media_type="application/json",
    )


def validation_exception_handler(exc):
    """
    handle data validation exceptions raised by the application
    : param exc: the exception
    """
    fields = [(*error.get("loc"), error.get("msg")) for error in exc.errors()]
    return JSONResponse(
        content=exception_message(
            error="ValidationException",
            message=f"invalid fields {fields}",
            internal_code=status.HTTP_400_BAD_REQUEST,
        ),
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="application/json",
    )


def app_exception_handler(exc):
    """
    handle any other exceptions raised by the application
    :param exc: the exception message
    """
    return JSONResponse(
        content=exception_message(
            error=exc.exception_case,
            message=exc.error_message,
            internal_code=exc.internal_code,
        ),
        status_code=exc.status_code,
        media_type="application/json",
    )

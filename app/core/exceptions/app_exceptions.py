from typing import Any, Union

from fastapi.logger import logger


class AppExceptionCase(Exception):
    """
    base exception to be raised by the application
    """

    def __init__(
        self,
        status_code: int,
        internal_code: Union[int, None],
        error_message: Any,
        context=None,
    ):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.internal_code = internal_code
        self.error_message = error_message
        self.context = context
        logger.critical(self.context) if self.context else None

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code = {self.status_code} - error_message = {self.error_message}>"
        )


class AppException:
    """
    the various exceptions that will be raised by the application
    """

    class BadRequestException(AppExceptionCase):
        def __init__(self, error_message, internal_code=None, context=None):
            """
            exception to catch errors caused by invalid requests
            :param error_message: the message return from request
            :param context: other message suitable for troubleshooting errors
            """

            status_code = 400
            super().__init__(status_code, internal_code, error_message, context=context)

    class InternalServerException(AppExceptionCase):
        """
        exception to catch errors caused by servers inability to process an operation
        :param error_message: the message return from request
        :param context: other message suitable for troubleshooting errors
        """

        def __init__(self, error_message, internal_code=None, context=None):
            status_code = 500
            super().__init__(status_code, internal_code, error_message, context=context)

    class ResourceExistException(AppExceptionCase):
        """
        exception to catch errors caused by resource duplication
        :param error_message: the message return from request
        :param context: other message suitable for troubleshooting errors
        """

        def __init__(self, error_message, internal_code=None, context=None):
            status_code = 409
            super().__init__(status_code, internal_code, error_message, context=context)

    class NotFoundException(AppExceptionCase):
        def __init__(self, error_message, internal_code=None, context=None):
            """
            exception to catch errors caused by resource nonexistence
            :param error_message: the message return from request
            :param context: other message suitable for troubleshooting errors
            """

            status_code = 404
            super().__init__(status_code, internal_code, error_message, context=context)

    class UnauthorizedException(AppExceptionCase):
        def __init__(self, error_message, internal_code=None, context=None):
            """
            exception to catch errors caused by illegitimate operation
            :param error_message: the message return from request
            :param context: other message suitable for troubleshooting errors
            """

            status_code = 401
            super().__init__(status_code, internal_code, error_message, context=context)

    class PermissionException(AppExceptionCase):
        def __init__(self, error_message, internal_code=None, context=None):
            """
            exception to catch errors caused by illegitimate operation
            :param error_message: the message return from request
            :param context: other message suitable for troubleshooting errors
            """

            status_code = 403
            super().__init__(status_code, internal_code, error_message, context=context)

    class ValidationException(AppExceptionCase):
        """
        exception the catch errors caused by invalid data
        :param error_message: the message return from request
        :param context: other message suitable for troubleshooting errors
        """

        def __init__(self, error_message, internal_code=None, context=None):
            status_code = 422
            super().__init__(status_code, internal_code, error_message, context=context)

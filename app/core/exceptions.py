
class AppException(Exception):
    """
    Base exception for application-level errors.
    """

    def __init__(
        self,
        message: str = "Application error",
        status_code: int = 500,
        error_code: str = "APP_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

        super().__init__(message)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
        )


class UnprocessableEntityException(AppException):
    def __init__(self, message: str = "Invalid data"):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
        )

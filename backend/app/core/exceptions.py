from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    detail = "Application error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class EmailAlreadyRegisteredError(AppError):
    status_code = 409
    detail = "Ten adres email jest już zarejestrowany"


class InvalidCredentialsError(AppError):
    status_code = 401
    detail = "Nieprawidłowy email lub hasło"


class InvalidTokenError(AppError):
    status_code = 401
    detail = "Invalid or expired token"


class InactiveUserError(AppError):
    status_code = 403
    detail = "User account is inactive"


class InsufficientRoleError(AppError):
    status_code = 403
    detail = "Insufficient permissions"


class ApplicationNotFoundError(AppError):
    status_code = 404
    detail = "Application not found"


class ApplicationNotEditableError(AppError):
    status_code = 409
    detail = "Application can only be edited while pending or needs changes"


class InvalidStatusTransitionError(AppError):
    status_code = 409
    detail = "Application is not in a state that allows this transition"


class UserNotFoundError(AppError):
    status_code = 404
    detail = "User not found"


class CannotModifyOwnAccountError(AppError):
    status_code = 409
    detail = "You cannot delete or change the role of your own account"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

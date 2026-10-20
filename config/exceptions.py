class AppError(Exception):
    status_code: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        return self._message

class NotFoundError(AppError):
    status_code = 404

class ConflictError(AppError):
    status_code = 409

class BusinessRuleError(AppError):
    status_code = 422
"""
Custom error classes for the Polymarket Copy Trading Bot
"""


class AppError(Exception):
    """Base error class for all application errors"""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        is_operational: bool = True,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.is_operational = is_operational


class ConfigurationError(AppError):
    """Configuration error - thrown when environment variables or config are invalid"""

    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR", 500, True)


class ValidationError(AppError):
    """Validation error - thrown when input validation fails"""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, "VALIDATION_ERROR", 400, True)
        self.field = field


class NetworkError(AppError):
    """Network error - thrown when API calls fail"""

    def __init__(self, message: str, original_error: Exception | None = None, url: str | None = None):
        super().__init__(message, "NETWORK_ERROR", 503, True)
        self.original_error = original_error
        self.url = url


class TradingError(AppError):
    """Trading error - thrown when trade execution fails"""

    def __init__(self, message: str, trade_id: str | None = None, asset: str | None = None):
        super().__init__(message, "TRADING_ERROR", 500, True)
        self.trade_id = trade_id
        self.asset = asset


class DatabaseError(AppError):
    """Database error - thrown when database operations fail"""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message, "DATABASE_ERROR", 500, True)
        self.original_error = original_error


class InsufficientFundsError(AppError):
    """Insufficient funds error - thrown when balance is too low"""

    def __init__(
        self,
        message: str,
        required_amount: float | None = None,
        available_amount: float | None = None,
    ):
        super().__init__(message, "INSUFFICIENT_FUNDS", 402, True)
        self.required_amount = required_amount
        self.available_amount = available_amount


def is_operational_error(error: Exception) -> bool:
    """Check if error is an operational error (expected error)"""
    return isinstance(error, AppError) and error.is_operational


def normalize_error(error: Exception) -> AppError:
    """Convert unknown error to AppError"""
    if isinstance(error, AppError):
        return error

    if isinstance(error, Exception):
        return AppError(str(error), "UNKNOWN_ERROR", 500, False)

    return AppError(f"Unknown error: {str(error)}", "UNKNOWN_ERROR", 500, False)

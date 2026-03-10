"""
Professional Error Handling Middleware

Centralized exception handling and error responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union
import traceback
from datetime import datetime

from .logging_config import app_logger as logger


class TalentRadarException(Exception):
    """Base exception for TalentRadar application."""
    
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ScraperException(TalentRadarException):
    """Exception raised during scraping operations."""
    pass


class DatabaseException(TalentRadarException):
    """Exception raised during database operations."""
    pass


class ValidationException(TalentRadarException):
    """Exception raised during data validation."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)


class APILimitException(TalentRadarException):
    """Exception raised when API rate limits are hit."""
    
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(
            message,
            status_code=429,
            details={"retry_after": retry_after}
        )


def create_error_response(
    status_code: int,
    message: str,
    error_type: str,
    details: dict = None,
    request_path: str = None
) -> dict:
    """
    Create standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        error_type: Type of error (validation, database, scraper, etc.)
        details: Additional error details
        request_path: Request path that caused the error
    
    Returns:
        dict: Standardized error response
    """
    return {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request_path,
            "details": details or {},
        }
    }


async def talentradar_exception_handler(request: Request, exc: TalentRadarException):
    """Handler for custom TalentRadar exceptions."""
    logger.error(
        f"TalentRadar Exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": str(request.url),
            "details": exc.details,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_type=exc.__class__.__name__,
            details=exc.details,
            request_path=str(request.url.path),
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors."""
    errors = exc.errors()
    
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={"errors": errors}
    )
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            status_code=422,
            message="Request validation failed",
            error_type="ValidationError",
            details={"validation_errors": errors},
            request_path=str(request.url.path),
        ),
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
    """Handler for HTTP exceptions."""
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={"path": str(request.url.path)}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_type="HTTPException",
            request_path=str(request.url.path),
        ),
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for uncaught exceptions."""
    # Log full traceback
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": str(request.url.path),
            "traceback": traceback.format_exc(),
        },
        exc_info=True,
    )
    
    # Check production mode from environment
    import os
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    if is_production:
        message = "An internal server error occurred"
        details = {}
    else:
        message = str(exc)
        details = {"traceback": traceback.format_exc()}
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            message=message,
            error_type="InternalServerError",
            details=details,
            request_path=str(request.url.path),
        ),
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app.
    
    Usage:
        from fastapi import FastAPI
        from app.utils.error_handling import register_exception_handlers
        
        app = FastAPI()
        register_exception_handlers(app)
    """
    app.add_exception_handler(TalentRadarException, talentradar_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully")

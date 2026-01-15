"""
Core package - Database and common utilities.
"""
from app.services.core.database import AsyncSessionLocal, engine, get_db
from app.services.core.exceptions import (
    AppException,
    ApplicationNotFoundError,
    ApplicationNotInProgressError,
    SessionNotFoundError,
    SessionAlreadyExistsError,
    NoTranscriptError,
    FileUploadError,
    FileTooLargeError,
    InvalidFileTypeError,
    AuthenticationError,
    AuthorizationError,
    AIServiceError,
)
from app.services.core.dependencies import (
    get_application_repo,
    get_session_repo,
    get_unit_of_work,
    UnitOfWork,
)

__all__ = [
    # Database
    "AsyncSessionLocal",
    "engine",
    "get_db",
    # Exceptions
    "AppException",
    "ApplicationNotFoundError",
    "ApplicationNotInProgressError",
    "SessionNotFoundError",
    "SessionAlreadyExistsError",
    "NoTranscriptError",
    "FileUploadError",
    "FileTooLargeError",
    "InvalidFileTypeError",
    "AuthenticationError",
    "AuthorizationError",
    "AIServiceError",
    # Dependencies
    "get_application_repo",
    "get_session_repo",
    "get_unit_of_work",
    "UnitOfWork",
]

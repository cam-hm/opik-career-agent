"""
Custom exceptions for the application.

Provides a consistent error handling pattern across the codebase.
"""
from typing import Optional


class AppException(Exception):
    """
    Base exception for application errors.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self, 
        code: str, 
        message: str, 
        status_code: int = 400,
        detail: Optional[str] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


# ===== Application Errors =====

class ApplicationNotFoundError(AppException):
    """Raised when an application is not found."""
    
    def __init__(self, application_id: str):
        super().__init__(
            code="APPLICATION_NOT_FOUND",
            message=f"Application {application_id} not found",
            status_code=404
        )


class ApplicationNotInProgressError(AppException):
    """Raised when trying to modify an application that's not in progress."""
    
    def __init__(self, application_id: str, current_status: str):
        super().__init__(
            code="APPLICATION_NOT_IN_PROGRESS",
            message=f"Application {application_id} is not in progress",
            status_code=400,
            detail=f"Current status: {current_status}"
        )


# ===== Interview/Session Errors =====

class SessionNotFoundError(AppException):
    """Raised when an interview session is not found."""
    
    def __init__(self, session_id: str):
        super().__init__(
            code="SESSION_NOT_FOUND",
            message=f"Session {session_id} not found",
            status_code=404
        )


class SessionAlreadyExistsError(AppException):
    """Raised when trying to create a session that already exists."""
    
    def __init__(self, session_id: str):
        super().__init__(
            code="SESSION_ALREADY_EXISTS",
            message=f"Session {session_id} already exists",
            status_code=409
        )


class NoTranscriptError(AppException):
    """Raised when trying to generate feedback without a transcript."""
    
    def __init__(self, session_id: str):
        super().__init__(
            code="NO_TRANSCRIPT",
            message="No transcript available for this session",
            status_code=400,
            detail=f"Session {session_id} has no recorded conversation"
        )


# ===== Upload/File Errors =====

class FileUploadError(AppException):
    """Raised when file upload fails."""
    
    def __init__(self, reason: str):
        super().__init__(
            code="FILE_UPLOAD_ERROR",
            message=f"File upload failed: {reason}",
            status_code=400
        )


class FileTooLargeError(FileUploadError):
    """Raised when uploaded file exceeds size limit."""
    
    def __init__(self, max_size_mb: int):
        super().__init__(reason=f"File exceeds {max_size_mb}MB limit")
        self.code = "FILE_TOO_LARGE"


class InvalidFileTypeError(FileUploadError):
    """Raised when uploaded file has invalid type."""
    
    def __init__(self, allowed_types: list[str]):
        types_str = ", ".join(allowed_types)
        super().__init__(reason=f"Invalid file type. Allowed: {types_str}")
        self.code = "INVALID_FILE_TYPE"


# ===== Auth Errors =====

class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(self, reason: str = "Authentication failed"):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=reason,
            status_code=401
        )


class AuthorizationError(AppException):
    """Raised when user doesn't have permission."""
    
    def __init__(self, resource: str):
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=f"Not authorized to access {resource}",
            status_code=403
        )


# ===== AI/External Service Errors =====

class AIServiceError(AppException):
    """Raised when AI service (Gemini, Deepgram) fails."""
    
    def __init__(self, service: str, reason: str):
        super().__init__(
            code="AI_SERVICE_ERROR",
            message=f"{service} service error: {reason}",
            status_code=503
        )

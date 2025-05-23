from typing import Optional

class AutoSenderError(Exception):
    """Base exception for AutoSender errors."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class PageLoadError(AutoSenderError):
    """Raised when page loading fails."""
    pass

class FormFillError(AutoSenderError):
    """Raised when form filling fails."""
    pass

class FormSubmitError(AutoSenderError):
    """Raised when form submission fails."""
    pass

class NetworkError(AutoSenderError):
    """Raised when network-related operations fail."""
    pass

class ConfigurationError(AutoSenderError):
    """Raised when there are configuration-related issues."""
    pass 
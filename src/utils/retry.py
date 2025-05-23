import time
import logging
from functools import wraps
from typing import TypeVar, Callable, Any, Optional, Type, Union, Tuple
from ..exceptions import AutoSenderError

T = TypeVar('T')

class RetryContext:
    def __init__(self, max_retries: int, initial_delay: float, max_delay: float, backoff_factor: float):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.current_retry = 0
        self.last_error: Optional[Exception] = None

def with_retry(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that implements exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to increase delay between retries
        exceptions: Exception(s) to catch and retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            retry_context = RetryContext(max_retries, initial_delay, max_delay, backoff_factor)
            
            while retry_context.current_retry <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retry_context.last_error = e
                    retry_context.current_retry += 1
                    
                    if retry_context.current_retry > max_retries:
                        raise AutoSenderError(
                            f"Failed after {max_retries} retries. Last error: {str(e)}",
                            original_error=e
                        )
                    
                    delay = min(
                        initial_delay * (backoff_factor ** (retry_context.current_retry - 1)),
                        max_delay
                    )
                    
                    logging.warning(
                        f"Attempt {retry_context.current_retry}/{max_retries} failed. "
                        f"Retrying in {delay:.2f} seconds. Error: {str(e)}"
                    )
                    time.sleep(delay)
            
            raise AutoSenderError("Unexpected retry loop exit", original_error=retry_context.last_error)
        
        return wrapper
    return decorator

class ErrorTracker:
    def __init__(self):
        self.error_counts: dict[str, int] = {}
        self.total_errors = 0
    
    def log_error(self, error_type: str, error: Exception) -> None:
        """Track and log an error occurrence."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.total_errors += 1
        
        logging.error(
            f"Error occurred: {error_type} - {str(error)}. "
            f"Total errors: {self.total_errors}, "
            f"Type count: {self.error_counts[error_type]}"
        )
    
    def get_error_summary(self) -> dict[str, Any]:
        """Get a summary of all tracked errors."""
        return {
            "total_errors": self.total_errors,
            "error_counts": self.error_counts
        } 
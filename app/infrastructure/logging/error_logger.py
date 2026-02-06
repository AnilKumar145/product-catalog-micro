"""Error logging for application errors."""

import logging
import traceback
from datetime import datetime
from app.config.settings import get_settings


class ErrorLogger:
    """Error logger for tracking application errors."""
    
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger("error")
        handler = logging.FileHandler(settings.ERROR_LOG_FILE)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.ERROR)
    
    def log_error(self, error: Exception, context: dict = None):
        """Log error with context and traceback."""
        error_msg = f"Error: {str(error)}\nContext: {context}\nTraceback: {traceback.format_exc()}"
        self.logger.error(error_msg)


error_logger = ErrorLogger()

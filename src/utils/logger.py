"""
Logging system for PC Assistant
Provides file and console logging with rotation
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    """Centralized logging system"""
    
    def __init__(self, log_dir="logs", log_file="pc_assistant.log"):
        """Initialize logger with file and console handlers"""
        self.log_dir = log_dir
        self.log_file = log_file
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Create logger
        self.logger = logging.getLogger("PCAssistant")
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # File handler with rotation (10MB max, 5 backups)
        log_path = os.path.join(self.log_dir, self.log_file)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def log_operation(self, operation, details, success=True):
        """Log an operation with structured format"""
        status = "SUCCESS" if success else "FAILED"
        message = f"[{operation}] {status} - {details}"
        if success:
            self.info(message)
        else:
            self.error(message)


# Global logger instance
_logger_instance = None

def get_logger():
    """Get global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance

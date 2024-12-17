import os
import logging
from datetime import datetime

def setup_logging(timestamp, dryrun):
    """
    Set up logging configuration.
    Returns the log directory path.
    """
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up action log
    action_log_name = f"actions_{timestamp}{'_dryrun' if dryrun else ''}.log"
    action_logger = logging.getLogger('action_logger')
    action_handler = logging.FileHandler(os.path.join(log_dir, action_log_name))
    action_formatter = logging.Formatter('%(asctime)s - %(message)s')
    action_handler.setFormatter(action_formatter)
    action_logger.addHandler(action_handler)
    action_logger.setLevel(logging.INFO)
    
    # Set up error log
    error_log_name = f"errors_{timestamp}.log"
    error_logger = logging.getLogger('error_logger')
    error_handler = logging.FileHandler(os.path.join(log_dir, error_log_name))
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    error_logger.setLevel(logging.ERROR)
    
    return log_dir

def log_action(user, account, action, datetime_str=None):
    """
    Log user action.
    Format: user, account, action, datetime
    """
    if not datetime_str:
        datetime_str = datetime.now().isoformat()
    logger = logging.getLogger('action_logger')
    logger.info(f"{user}, {account}, {action}, {datetime_str}")

def log_error(message):
    """Log error message."""
    logger = logging.getLogger('error_logger')
    logger.error(message)

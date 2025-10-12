import logging
import os
from datetime import datetime

# Create logs directory
os.makedirs("/app/logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/crane-intelligence.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_api_call(endpoint: str, method: str, status_code: int, user_id: int = None):
    logger.info(f"API Call: {method} {endpoint} - Status: {status_code} - User: {user_id}")

def log_error(error: str, endpoint: str = None):
    logger.error(f"Error: {error} - Endpoint: {endpoint}")

def log_security_event(event: str, ip: str, user_id: int = None):
    logger.warning(f"Security Event: {event} - IP: {ip} - User: {user_id}")

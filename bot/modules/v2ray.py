import subprocess
from modules.logger import get_logger


logger = get_logger(__name__)


def is_service_active(service_name: str = "v2ray") -> bool:
    """Check if the service is active."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip() == "active"
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
        return False
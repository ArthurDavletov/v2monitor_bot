import json
import subprocess

from prettytable import PrettyTable

from .logger import get_logger

logger = get_logger(__name__)


def humanize_size(size: int) -> str:
    """Convert bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def is_service_active(service_name: str = "v2ray") -> bool:
    """Check if the service is active."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == "active"
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
        return False


def get_stats(server: str) -> str:
    """Get statistics of the v2ray service."""
    try:
        result = subprocess.run(
            [
                "v2ray", "api", "stats",
                f"--server={server}",
                "--json"
            ],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Error getting stats: {result.stderr.strip()}.")
            return "Error retrieving stats."
        # Parse the JSON output
        stats = []
        for line in json.loads(result.stdout.strip()).get("stat", {}):
            name = line.get("name", "")
            if not name:
                continue
            direction, target, _, t = name.split(">>>")
            if t == "downlink": t = "down"
            elif t == "uplink": t = "up"
            stats.append({
                "direction": direction.strip(),
                "target": target.strip(),
                "type": t.strip(),
                "value": line.get("value", 0)
            })
        if not stats:
            return "No statistics available."
        stats.sort(key=lambda x: (x.get("direction", ""), x.get("target", ""), x.get("type", "")))
        # Create a table to display the stats
        table = PrettyTable()
        table.field_names = ["Direction", "Target", "Type", "Value"]
        for item in stats:
            table.add_row([
                item.get("direction", ""),
                item.get("target", ""),
                item.get("type", ""),
                humanize_size(int(item.get("value", 0)))
            ])
        return str(table)
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return "Error retrieving stats."
import json
import subprocess

from prettytable import PrettyTable

from .logger import get_logger

logger = get_logger(__name__)


class NoStatsAvailable(Exception):
    pass


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


def get_table(server: str) -> PrettyTable:
    """Get a pretty table with stats.
    Types of the traffic were shorten (downlink -> down, uplink -> up).
    Bytes were converted to kilobytes, megabytes, etc.

    :param server: The v2ray API server

    Raises `NoStatsAvailable` if no stats are available."""
    stats = get_stats(server)
    if not stats:
        raise NoStatsAvailable("Stats are empty")
    stats.sort(key=lambda x: (x.get("direction", ""), x.get("target", ""), x.get("type", "")))
    # Create a table to display the stats
    table = PrettyTable()
    table.field_names = ["Direction", "Target", "Type", "Value"]
    for item in stats:
        direction = item.get("direction", "")
        if direction == "downlink": direction = "down"
        elif direction == "uplink": direction = "up"
        table.add_row([
            direction,
            item.get("target", ""),
            item.get("type", ""),
            humanize_size(int(item.get("value", 0)))
        ])
    return table


def get_stats(server: str) -> list[dict[str, int | float]]:
    """Get statistics of the v2ray service.

    :param server: API server

    :return: list of dicts from v2ray api service

    * direction - direction of the traffic (group)
    * target - target of the traffic (tag)
    * type - type of the traffic ("uplink" or "downlink")
    * value - bytes of the traffic
    """
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
        logger.error(f"Error getting stats: {result.stderr.strip()}. Return code: {result.returncode}.")
        raise NoStatsAvailable("Error getting stats")
    # Parse the JSON output
    stats = []
    for line in json.loads(result.stdout.strip()).get("stat", {}):
        name = line.get("name", "")
        if not name:
            logger.warning(f"There's no name of user: {line}")
            continue
        direction, target, _, t = name.split(">>>")
        stats.append({
            "direction": direction.strip(),
            "target": target.strip(),
            "type": t.strip(),
            "value": line.get("value", 0)
        })
    return stats

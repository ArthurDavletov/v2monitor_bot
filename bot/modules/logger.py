"""Logger module for the bot.
This module sets up a custom logger with rotating file handling and compression.
It includes a custom formatter that adds milliseconds to the timestamp and
compresses old log files into tar.gz archives.
"""
import logging
import os
import tarfile
from pathlib import Path
from logging.handlers import RotatingFileHandler
import time


class CustomFormatter(logging.Formatter):
    """Custom formatter with milliseconds in the timestamp and custom date format."""
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, dt)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", dt)
        return f"{s}.{int(record.msecs):03d}"


class CompressedRotatingFileHandler(RotatingFileHandler):
    """Handler that compresses old log files into a tar.gz archives."""
    def doRollover(self):
        super().doRollover()

        log_dir = Path(self.baseFilename).parent
        log_base = Path(self.baseFilename).name

        # archive old log files
        for i in range(self.backupCount, 0, -1):
            rotated_file = log_dir / f"{log_base}.{i}"
            if rotated_file.exists():
                archive_file = log_dir / f"{rotated_file.name}.tar.gz"
                with tarfile.open(archive_file, "w:gz") as tar:
                    tar.add(rotated_file, arcname=rotated_file.name)
                rotated_file.unlink()

        # remove old archives
        archives = sorted(
            log_dir.glob(f"{log_base}.*.tar.gz"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        for archive in archives[self.backupCount:]:
            archive.unlink()


LOG_FILE = Path(os.path.dirname(__file__)) / "logs" / "bot.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.setLevel(logging.DEBUG)

file_handler = CompressedRotatingFileHandler(
    LOG_FILE, maxBytes=10*1024*1024,
    backupCount=5, encoding="utf-8"
)
file_formatter = CustomFormatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S"
)

file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)


def get_logger(name):
    """Returns a logger with the specified name."""
    return logging.getLogger(name)

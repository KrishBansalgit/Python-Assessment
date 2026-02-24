import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_file: str = "bot.log") -> None:
    """
    Configure logging for the trading bot.

    - Logs INFO and above to console.
    - Logs DEBUG and above to a rotating log file.
    - Ensures idempotent configuration (safe to call multiple times).
    """
    if logging.getLogger().handlers:
        # Logging already configured
        return

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler (detailed logs)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler (concise runtime info)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Make python-binance chatty so we see request/response details
    binance_logger = logging.getLogger("binance")
    binance_logger.setLevel(logging.DEBUG)
    binance_logger.addHandler(file_handler)
    binance_logger.addHandler(console_handler)


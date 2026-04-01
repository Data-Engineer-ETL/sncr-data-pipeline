"""Structured logging configuration."""
import sys
import json
from pathlib import Path
from loguru import logger
from src.infrastructure.config import get_settings


def serialize_log(record: dict) -> str:
    """Serialize log record to JSON."""
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Add extra fields if present
    if record.get("extra"):
        subset["extra"] = record["extra"]
    
    # Add exception info if present
    if record["exception"]:
        subset["exception"] = {
            "type": record["exception"].type.__name__,
            "value": str(record["exception"].value),
        }
    
    return json.dumps(subset, default=str)


def setup_logging() -> None:
    """Configure structured logging with Loguru."""
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with color
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # Add file handler with JSON format
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "sncr_{time:YYYY-MM-DD}.log",
        level=settings.LOG_LEVEL,
        format=serialize_log,
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated logs
        serialize=False,  # We handle serialization manually
    )
    
    logger.info("Logging configured", level=settings.LOG_LEVEL)


# Configure logging on module import
setup_logging()

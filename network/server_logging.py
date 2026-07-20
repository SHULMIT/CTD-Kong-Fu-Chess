"""Structured, rotating, sensitive-data-safe server logging configuration."""

from __future__ import annotations

import json
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


_SENSITIVE_FRAGMENTS = ("password", "password_hash", "token", "resume_token")
_STANDARD_RECORD_KEYS = set(logging.makeLogRecord({}).__dict__)


class SensitiveDataFilter(logging.Filter):
    """Redact sensitive mapping values before any handler formats a record."""

    REDACTED = "[REDACTED]"
    _INLINE_SECRET = re.compile(
        r"(?i)(password(?:_hash)?|resume_token|token)\s*([=:])\s*([^\s,}]+)"
    )

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._sanitize(record.msg)
        record.args = self._sanitize(record.args)
        for key, value in tuple(record.__dict__.items()):
            if self._is_sensitive(key):
                setattr(record, key, self.REDACTED)
            elif key not in _STANDARD_RECORD_KEYS:
                setattr(record, key, self._sanitize(value))
        return True

    @classmethod
    def _sanitize(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: cls.REDACTED if cls._is_sensitive(str(key)) else cls._sanitize(item)
                for key, item in value.items()
            }
        if isinstance(value, tuple):
            return tuple(cls._sanitize(item) for item in value)
        if isinstance(value, list):
            return [cls._sanitize(item) for item in value]
        if isinstance(value, str):
            return cls._INLINE_SECRET.sub(
                lambda match: f"{match.group(1)}{match.group(2)}{cls.REDACTED}",
                value,
            )
        return value

    @staticmethod
    def _is_sensitive(key: str) -> bool:
        normalized = key.lower()
        return any(fragment in normalized for fragment in _SENSITIVE_FRAGMENTS)


class StructuredJsonFormatter(logging.Formatter):
    """Render each server record as one machine-readable JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event_type", record.getMessage()),
            "message": record.getMessage(),
        }
        for key in ("game_id", "user_id", "username", "room_code", "reason"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_server_logging(
    level: str = "INFO",
    log_file: str | Path = "data/server.log",
    max_bytes: int = 2_000_000,
    backup_count: int = 5,
) -> logging.Logger:
    """Configure console and rotating-file handlers for the server namespace."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unknown log level: {level}")
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("kung_fu_chess.server")
    logger.handlers.clear()
    logger.setLevel(numeric_level)
    logger.propagate = False
    formatter = StructuredJsonFormatter()
    sensitive_filter = SensitiveDataFilter()
    console = logging.StreamHandler()
    rotating_file = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    for handler in (console, rotating_file):
        handler.setLevel(numeric_level)
        handler.setFormatter(formatter)
        handler.addFilter(sensitive_filter)
        logger.addHandler(handler)
    return logger

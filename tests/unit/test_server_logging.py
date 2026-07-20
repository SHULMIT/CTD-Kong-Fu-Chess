"""Tests for structured rotating server logging and secret redaction."""

import json
import logging
from pathlib import Path

from network.server_logging import configure_server_logging


def test_console_and_rotating_file_logging_redact_sensitive_values(
    tmp_path: Path,
    capsys,
) -> None:
    log_file = tmp_path / "server.log"
    logger = configure_server_logging(
        level="DEBUG",
        log_file=log_file,
        max_bytes=256,
        backup_count=2,
    )

    logger.info(
        "authentication_attempt",
        extra={
            "event_type": "authentication_attempt",
            "username": "Dan",
            "password": "plain-secret",
            "resume_token": "resume-secret",
            "details": {"password_hash": "hash-secret", "safe": "value"},
        },
    )
    logger.warning("token=inline-secret password:another-secret")
    for handler in logger.handlers:
        handler.flush()

    output = capsys.readouterr().err + log_file.read_text(encoding="utf-8")
    assert "plain-secret" not in output
    assert "resume-secret" not in output
    assert "hash-secret" not in output
    assert "inline-secret" not in output
    assert "another-secret" not in output
    assert "[REDACTED]" in output
    assert '"username": "Dan"' in output
    assert any(handler.__class__.__name__ == "RotatingFileHandler" for handler in logger.handlers)


def test_structured_formatter_includes_event_context(tmp_path: Path) -> None:
    log_file = tmp_path / "structured.log"
    logger = configure_server_logging(log_file=log_file)
    logger.info(
        "room_created",
        extra={
            "event_type": "room_created",
            "game_id": "game-1",
            "user_id": 7,
            "room_code": "AB42KF",
        },
    )
    for handler in logger.handlers:
        handler.flush()

    record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[-1])
    assert record["event"] == "room_created"
    assert record["game_id"] == "game-1"
    assert record["user_id"] == 7
    assert record["room_code"] == "AB42KF"


def test_invalid_log_level_is_rejected(tmp_path: Path) -> None:
    try:
        configure_server_logging("NOT_A_LEVEL", tmp_path / "server.log")
    except ValueError as error:
        assert "Unknown log level" in str(error)
    else:
        raise AssertionError("Invalid logging levels must not be accepted")

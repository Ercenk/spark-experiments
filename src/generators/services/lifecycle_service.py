"""Lifecycle command service wrapping pause/resume operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from src.generators.lifecycle import GeneratorLifecycle


@dataclass
class CommandResult:
    success: bool
    action: str
    status: str
    timestamp: str
    message: Optional[str] = None
    error: Optional[str] = None
    extra: Dict[str, Any] = None  # type: ignore


class LifecycleCommandService:
    def __init__(self, lifecycle: GeneratorLifecycle) -> None:
        self.lifecycle = lifecycle

    def pause(self) -> CommandResult:
        if self.lifecycle.paused:
            return CommandResult(
                success=True,
                action="pause",
                status="paused",
                timestamp=datetime.now(timezone.utc).isoformat(),
                message="Already paused",
                extra={},
            )
        self.lifecycle.pause()
        return CommandResult(
            success=True,
            action="pause",
            status="paused",
            timestamp=datetime.now(timezone.utc).isoformat(),
            message="Paused successfully",
            extra={},
        )

    def resume(self) -> CommandResult:
        if not self.lifecycle.paused:
            return CommandResult(
                success=True,
                action="resume",
                status="running",
                timestamp=datetime.now(timezone.utc).isoformat(),
                message="Already running",
                extra={},
            )
        self.lifecycle.resume()
        return CommandResult(
            success=True,
            action="resume",
            status="running",
            timestamp=datetime.now(timezone.utc).isoformat(),
            message="Resumed successfully",
            extra={},
        )

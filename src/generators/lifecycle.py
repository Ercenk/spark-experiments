"""Generator lifecycle management with pause/resume support."""

import signal
import threading
from datetime import datetime, timezone
from typing import Optional


class GeneratorLifecycle:
    """
    Manages generator lifecycle with pause/resume and graceful shutdown.
    
    Provides:
    - Pause/resume state management
    - Signal handler registration
    - Thread-safe state access
    - Graceful shutdown coordination
    """
    
    def __init__(self):
        """Initialize lifecycle manager."""
        self.paused: bool = False
        self.should_exit: bool = False
        self.pause_event: threading.Event = threading.Event()
        self.pause_event.set()  # Initially not paused
        
        self._lock: threading.Lock = threading.Lock()
        self._pause_time: Optional[datetime] = None
        self._resume_time: Optional[datetime] = None
        
    def register_signal_handlers(self, logger=None) -> None:
        """
        Register signal handlers for pause/resume/shutdown.
        
        Args:
            logger: Optional logger for state transitions
            
        Signals:
            SIGUSR1: Pause generation
            SIGUSR2: Resume generation
            SIGTERM/SIGINT: Graceful shutdown
        """
        def handle_pause(signum, frame):
            """Handle SIGUSR1 - pause generation."""
            with self._lock:
                if not self.paused:
                    self.paused = True
                    self._pause_time = datetime.now(timezone.utc)
                    self.pause_event.clear()
                    if logger:
                        logger.info(
                            "Generation PAUSED",
                            metadata={
                                "signal": "SIGUSR1",
                                "pause_time": self._pause_time.isoformat()
                            }
                        )
        
        def handle_resume(signum, frame):
            """Handle SIGUSR2 - resume generation."""
            with self._lock:
                if self.paused:
                    self.paused = False
                    self._resume_time = datetime.now(timezone.utc)
                    self.pause_event.set()
                    if logger:
                        pause_duration = (self._resume_time - self._pause_time).total_seconds() if self._pause_time else 0
                        logger.info(
                            "Generation RESUMED",
                            metadata={
                                "signal": "SIGUSR2",
                                "resume_time": self._resume_time.isoformat(),
                                "pause_duration_seconds": pause_duration
                            }
                        )
        
        def handle_shutdown(signum, frame):
            """Handle SIGTERM/SIGINT - graceful shutdown."""
            with self._lock:
                self.should_exit = True
                self.pause_event.set()  # Wake up any waiting threads
                if logger:
                    logger.info(
                        "Shutdown signal received",
                        metadata={
                            "signal": "SIGTERM" if signum == signal.SIGTERM else "SIGINT",
                            "shutdown_time": datetime.now(timezone.utc).isoformat()
                        }
                    )
        
        signal.signal(signal.SIGUSR1, handle_pause)
        signal.signal(signal.SIGUSR2, handle_resume)
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
    
    def pause(self) -> None:
        """Pause generation programmatically (not via signal)."""
        with self._lock:
            if not self.paused:
                self.paused = True
                self._pause_time = datetime.now(timezone.utc)
                self.pause_event.clear()
    
    def resume(self) -> None:
        """Resume generation programmatically (not via signal)."""
        with self._lock:
            if self.paused:
                self.paused = False
                self._resume_time = datetime.now(timezone.utc)
                self.pause_event.set()
    
    def is_paused(self) -> bool:
        """Check if generation is paused."""
        with self._lock:
            return self.paused
    
    def should_shutdown(self) -> bool:
        """Check if shutdown is requested."""
        with self._lock:
            return self.should_exit
    
    def wait_if_paused(self, timeout: Optional[float] = None) -> bool:
        """
        Wait if paused, return immediately if not paused or shutdown requested.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            True if should continue, False if should exit
        """
        if self.should_exit:
            return False
        
        # Wait for pause_event to be set (not paused)
        self.pause_event.wait(timeout=timeout)
        
        return not self.should_exit
    
    def get_state(self) -> dict:
        """
        Get current lifecycle state.
        
        Returns:
            Dictionary with state information
        """
        with self._lock:
            return {
                "paused": self.paused,
                "should_exit": self.should_exit,
                "pause_time": self._pause_time.isoformat() if self._pause_time else None,
                "resume_time": self._resume_time.isoformat() if self._resume_time else None
            }

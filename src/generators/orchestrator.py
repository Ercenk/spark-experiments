"""Generator orchestrator for coordinating company and driver generators."""

import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from src.generators.lifecycle import GeneratorLifecycle


class GeneratorOrchestrator:
    """
    Orchestrates multiple generators with shared lifecycle management.
    
    Manages:
    - Thread spawning for each generator
    - Shared pause/resume state
    - Coordinated shutdown
    """
    
    def __init__(self, lifecycle: GeneratorLifecycle):
        """
        Initialize orchestrator.
        
        Args:
            lifecycle: Shared lifecycle manager
        """
        self.lifecycle = lifecycle
        self.threads: list[threading.Thread] = []
    
    def add_generator(self, name: str, target: Callable, args: tuple = ()) -> None:
        """
        Add a generator function to orchestrate.
        
        Args:
            name: Generator name for logging
            target: Generator function to run
            args: Arguments to pass to generator function
        """
        thread = threading.Thread(target=target, args=args, name=name, daemon=False)
        self.threads.append(thread)
    
    def start(self) -> None:
        """Start all registered generator threads."""
        for thread in self.threads:
            thread.start()
    
    def wait(self) -> None:
        """Wait for all generator threads to complete."""
        for thread in self.threads:
            thread.join()
    
    @staticmethod
    def align_to_interval(timestamp: datetime, interval_seconds: float) -> datetime:
        """
        Align timestamp to interval boundary based on seconds since epoch.
        
        Args:
            timestamp: Timestamp to align
            interval_seconds: Interval duration in seconds
            
        Returns:
            Aligned timestamp at interval boundary
            
        Example:
            interval_seconds=600 (10min) at 12:17:34 -> 12:10:00
            interval_seconds=10 (10sec) at 12:17:34 -> 12:17:30
        """
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        seconds_since_epoch = (timestamp - epoch).total_seconds()
        aligned_seconds = (seconds_since_epoch // interval_seconds) * interval_seconds
        return epoch + timedelta(seconds=aligned_seconds)
    
    @staticmethod
    def wait_for_next_interval(
        target_time: datetime,
        lifecycle: GeneratorLifecycle,
        check_interval_seconds: float = 1.0,
        emulated_mode: bool = False
    ) -> bool:
        """
        Sleep until target_time, respecting pause state and shutdown requests.
        
        Args:
            target_time: Target datetime to wait until
            lifecycle: Lifecycle manager to check for pause/shutdown
            check_interval_seconds: How often to check state (default 1s production, 0.5s emulated)
            emulated_mode: If True, use faster check interval for responsiveness
            
        Returns:
            True if reached target_time normally, False if interrupted by shutdown
        """
        # Use faster check interval in emulated mode for better responsiveness
        check_interval = 0.5 if emulated_mode else check_interval_seconds
        
        while datetime.now(timezone.utc) < target_time:
            # Check for shutdown
            if lifecycle.should_shutdown():
                return False
            
            # Wait if paused (with timeout to periodically recheck)
            if not lifecycle.wait_if_paused(timeout=check_interval):
                return False
            
            # Sleep for check_interval or until target_time, whichever is shorter
            remaining = (target_time - datetime.now(timezone.utc)).total_seconds()
            if remaining > 0:
                sleep_duration = min(remaining, check_interval)
                time.sleep(sleep_duration)
            else:
                break
        
        return not lifecycle.should_shutdown()

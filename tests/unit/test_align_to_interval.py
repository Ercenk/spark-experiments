"""Unit tests for align_to_interval helper function."""

import pytest
from datetime import datetime, timedelta, timezone
from src.generators.orchestrator import GeneratorOrchestrator


class TestAlignToInterval:
    """Test align_to_interval second-level precision."""
    
    def test_align_to_10_second_intervals(self):
        """Test alignment to 10-second boundaries."""
        # Test cases: (input time, expected aligned time)
        test_cases = [
            # Already aligned
            (datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc), 
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            # Mid-interval
            (datetime(2025, 11, 9, 12, 0, 5, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            # Just before next boundary
            (datetime(2025, 11, 9, 12, 0, 9, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            # Various positions
            (datetime(2025, 11, 9, 12, 17, 34, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 17, 30, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 17, 40, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 17, 40, tzinfo=timezone.utc)),
        ]
        
        for input_time, expected in test_cases:
            result = GeneratorOrchestrator.align_to_interval(input_time, 10.0)
            assert result == expected, f"For {input_time}, expected {expected} but got {result}"
    
    def test_align_to_5_second_intervals(self):
        """Test alignment to 5-second boundaries."""
        test_cases = [
            (datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 0, 3, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 0, 7, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 5, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 17, 34, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 17, 30, tzinfo=timezone.utc)),
        ]
        
        for input_time, expected in test_cases:
            result = GeneratorOrchestrator.align_to_interval(input_time, 5.0)
            assert result == expected
    
    def test_align_to_1_second_intervals(self):
        """Test alignment to 1-second boundaries (minimum supported)."""
        # 1-second intervals should align to the second (floor microseconds)
        test_cases = [
            (datetime(2025, 11, 9, 12, 0, 0, 123456, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 0, 5, 999999, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 5, tzinfo=timezone.utc)),
        ]
        
        for input_time, expected in test_cases:
            result = GeneratorOrchestrator.align_to_interval(input_time, 1.0)
            assert result == expected
    
    def test_align_to_60_second_intervals(self):
        """Test alignment to 60-second (1 minute) boundaries."""
        test_cases = [
            (datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 0, 30, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 17, 45, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 17, 0, tzinfo=timezone.utc)),
        ]
        
        for input_time, expected in test_cases:
            result = GeneratorOrchestrator.align_to_interval(input_time, 60.0)
            assert result == expected
    
    def test_align_to_600_second_intervals(self):
        """Test alignment to 600-second (10 minute) boundaries."""
        test_cases = [
            (datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 17, 34, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 10, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 25, 0, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 20, 0, tzinfo=timezone.utc)),
        ]
        
        for input_time, expected in test_cases:
            result = GeneratorOrchestrator.align_to_interval(input_time, 600.0)
            assert result == expected
    
    def test_align_to_3600_second_intervals(self):
        """Test alignment to 3600-second (1 hour) boundaries."""
        test_cases = [
            (datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 12, 30, 0, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 12, 0, 0, tzinfo=timezone.utc)),
            
            (datetime(2025, 11, 9, 13, 45, 30, tzinfo=timezone.utc),
             datetime(2025, 11, 9, 13, 0, 0, tzinfo=timezone.utc)),
        ]
        
        for input_time, expected in test_cases:
            result = GeneratorOrchestrator.align_to_interval(input_time, 3600.0)
            assert result == expected
    
    def test_align_preserves_timezone(self):
        """Test that aligned result preserves UTC timezone."""
        input_time = datetime(2025, 11, 9, 12, 17, 34, tzinfo=timezone.utc)
        result = GeneratorOrchestrator.align_to_interval(input_time, 10.0)
        
        assert result.tzinfo == timezone.utc
        assert result == datetime(2025, 11, 9, 12, 17, 30, tzinfo=timezone.utc)
    
    def test_align_across_minute_boundary(self):
        """Test alignment across minute boundaries."""
        # 10-second intervals at 12:00:55 should align to 12:00:50
        input_time = datetime(2025, 11, 9, 12, 0, 55, tzinfo=timezone.utc)
        result = GeneratorOrchestrator.align_to_interval(input_time, 10.0)
        assert result == datetime(2025, 11, 9, 12, 0, 50, tzinfo=timezone.utc)
        
        # 10-second intervals at 12:01:03 should align to 12:01:00
        input_time = datetime(2025, 11, 9, 12, 1, 3, tzinfo=timezone.utc)
        result = GeneratorOrchestrator.align_to_interval(input_time, 10.0)
        assert result == datetime(2025, 11, 9, 12, 1, 0, tzinfo=timezone.utc)
    
    def test_align_across_hour_boundary(self):
        """Test alignment across hour boundaries."""
        # 10-second intervals at 12:59:57 should align to 12:59:50
        input_time = datetime(2025, 11, 9, 12, 59, 57, tzinfo=timezone.utc)
        result = GeneratorOrchestrator.align_to_interval(input_time, 10.0)
        assert result == datetime(2025, 11, 9, 12, 59, 50, tzinfo=timezone.utc)
        
        # 10-second intervals at 13:00:03 should align to 13:00:00
        input_time = datetime(2025, 11, 9, 13, 0, 3, tzinfo=timezone.utc)
        result = GeneratorOrchestrator.align_to_interval(input_time, 10.0)
        assert result == datetime(2025, 11, 9, 13, 0, 0, tzinfo=timezone.utc)
    
    def test_deterministic_alignment(self):
        """Test that same input always produces same output."""
        input_time = datetime(2025, 11, 9, 12, 17, 34, tzinfo=timezone.utc)
        
        results = [
            GeneratorOrchestrator.align_to_interval(input_time, 10.0)
            for _ in range(10)
        ]
        
        # All results should be identical
        assert len(set(results)) == 1
        assert results[0] == datetime(2025, 11, 9, 12, 17, 30, tzinfo=timezone.utc)

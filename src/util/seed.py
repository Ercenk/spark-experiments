"""Seed management utilities for reproducible data generation."""

import json
import os
import random
from pathlib import Path
from typing import Optional


def generate_or_load_seed(manifest_path: str, provided_seed: Optional[int] = None) -> int:
    """
    Generate or load seed for reproducible data generation.
    
    Args:
        manifest_path: Path to manifest file for storing/loading seed
        provided_seed: Optional explicit seed value; if None, generates or loads from manifest
        
    Returns:
        int: Seed value to use for random generation
        
    Behavior:
        - If provided_seed is given, uses that value and updates manifest
        - If manifest exists and contains seed, loads from manifest
        - Otherwise, generates new random seed and writes to manifest
    """
    manifest_file = Path(manifest_path)
    
    # If explicit seed provided, use it and update manifest
    if provided_seed is not None:
        _write_seed_to_manifest(manifest_file, provided_seed)
        return provided_seed
    
    # Try to load from existing manifest
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r') as f:
                data = json.load(f)
                if 'seed' in data:
                    return data['seed']
        except (json.JSONDecodeError, KeyError, IOError):
            pass  # Fall through to generate new seed
    
    # Generate new seed
    new_seed = random.randint(1, 2**31 - 1)
    _write_seed_to_manifest(manifest_file, new_seed)
    return new_seed


def _write_seed_to_manifest(manifest_file: Path, seed: int) -> None:
    """Write seed to manifest file, preserving other fields if present."""
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing data if present
    data = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # Start with empty dict
    
    # Update seed and write
    data['seed'] = seed
    with open(manifest_file, 'w') as f:
        json.dump(data, f, indent=2)

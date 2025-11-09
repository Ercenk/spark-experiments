"""Pytest configuration ensuring project root is on sys.path for 'src' package imports.

Tests import modules using the pattern 'from src....'. When running pytest from
the repository root, we need to add the root to sys.path so that the 'src'
package (located at root/src) is discoverable.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
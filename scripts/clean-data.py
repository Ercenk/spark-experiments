#!/usr/bin/env python3
"""Clean all generated data files and start fresh.

This script removes all JSON batches from data/raw/ and data/manifests/,
preserving the directory structure. Useful for starting a new experiment
or resetting the simulation state.

Usage:
    python scripts/clean-data.py [--confirm]
    
Options:
    --confirm  Skip confirmation prompt and proceed with cleanup
"""

import argparse
import shutil
import sys
from pathlib import Path


def clean_data(confirm: bool = False) -> None:
    """
    Clean all generated data files.
    
    Args:
        confirm: If True, skip confirmation prompt
    """
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    # Define paths to clean
    paths_to_clean = {
        "Companies file": data_dir / "raw" / "companies.jsonl",
        "Event batches": data_dir / "raw" / "events",
        "Seed manifest": data_dir / "manifests" / "seed_manifest.json",
        "Batch manifest": data_dir / "manifests" / "batch_manifest.json",
        "Generator state": data_dir / "manifests" / "generator_state.json",
        "Dataset descriptor": data_dir / "manifests" / "dataset.md",
        "Logs": data_dir / "manifests" / "logs",
    }
    
    # Check what exists
    existing_paths = {name: path for name, path in paths_to_clean.items() if path.exists()}
    
    if not existing_paths:
        print("✓ No data files found - nothing to clean")
        return
    
    # Show what will be deleted
    print("The following will be deleted:")
    print()
    for name, path in existing_paths.items():
        if path.is_file():
            size = path.stat().st_size
            print(f"  • {name}: {path} ({size:,} bytes)")
        else:
            # Count files in directory
            files = list(path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            print(f"  • {name}: {path} ({file_count} files)")
    print()
    
    # Confirm deletion
    if not confirm:
        response = input("Proceed with deletion? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cancelled - no files deleted")
            return
    
    # Perform cleanup
    deleted_count = 0
    for name, path in existing_paths.items():
        try:
            if path.is_file():
                path.unlink()
                print(f"✓ Deleted {name}")
                deleted_count += 1
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"✓ Deleted {name} directory")
                deleted_count += 1
        except Exception as e:
            print(f"✗ Failed to delete {name}: {e}", file=sys.stderr)
    
    # Ensure directories exist
    (data_dir / "raw").mkdir(parents=True, exist_ok=True)
    (data_dir / "manifests").mkdir(parents=True, exist_ok=True)
    (data_dir / "staged").mkdir(parents=True, exist_ok=True)
    (data_dir / "processed").mkdir(parents=True, exist_ok=True)
    
    print()
    print(f"✓ Cleanup complete - {deleted_count} items deleted")
    print("✓ Directory structure preserved")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Clean all generated data files and start fresh",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/clean-data.py              # Interactive mode with confirmation
    python scripts/clean-data.py --confirm    # Skip confirmation
    
Note: This preserves the directory structure but removes all generated data files.
      The generator container must be restarted after cleanup to reinitialize.
        """
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    try:
        clean_data(confirm=args.confirm)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

"""Data loader that uses GitHub Dataset folder.

This module provides functions to load data from the GitHub Dataset folder
instead of mock data.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Dataset paths
DATASET_ROOT = Path(__file__).parent / "dataset"
MOCK_ROOT = Path(__file__).parent / "mock"


def load_from_dataset(filename: str) -> Dict[str, Any]:
    """Load data from GitHub Dataset folder.
    
    Args:
        filename: Name of the file to load (e.g., "valid_msme_input.json")
        
    Returns:
        Loaded data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist in dataset
    """
    # Try dataset folder first
    dataset_path = DATASET_ROOT / filename
    
    if dataset_path.exists():
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        print(f"📁 Loaded from dataset: {filename}")
        return data
    
    # Fallback to mock data
    mock_path = MOCK_ROOT / filename
    if mock_path.exists():
        with open(mock_path, 'r') as f:
            data = json.load(f)
        print(f"⚠️  Loaded from mock (dataset not found): {filename}")
        return data
    
    raise FileNotFoundError(f"File not found in dataset or mock: {filename}")


def list_dataset_files() -> List[str]:
    """List all files in the dataset folder."""
    if not DATASET_ROOT.exists():
        return []
    
    files = []
    for file_path in DATASET_ROOT.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(DATASET_ROOT)
            files.append(str(rel_path))
    
    return files


def get_dataset_info() -> Dict[str, Any]:
    """Get information about the dataset."""
    info = {
        "dataset_root": str(DATASET_ROOT),
        "exists": DATASET_ROOT.exists(),
        "files": list_dataset_files() if DATASET_ROOT.exists() else [],
        "file_count": len(list_dataset_files()) if DATASET_ROOT.exists() else 0
    }
    
    return info


if __name__ == "__main__":
    # Test data loader
    info = get_dataset_info()
    print("Dataset Info:")
    print(f"  Root: {info['dataset_root']}")
    print(f"  Exists: {info['exists']}")
    print(f"  File Count: {info['file_count']}")
    
    if info['files']:
        print("\nFiles:")
        for file in info['files']:
            print(f"  - {file}")

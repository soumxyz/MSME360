"""Script to import dataset from GitHub repository instead of using mock data.

This script configures the system to use the Dataset folder from the GitHub
main branch instead of locally generated mock data.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Dataset configuration
GITHUB_DATASET_PATH = "/Users/utkarshsinha/Desktop/MSME360/Dataset"
LOCAL_DATA_PATH = "/Users/utkarshsinha/Desktop/MSME360/risk agent/data"


def check_dataset_exists():
    """Check if Dataset folder exists."""
    if not os.path.exists(GITHUB_DATASET_PATH):
        print(f"❌ Dataset folder not found at: {GITHUB_DATASET_PATH}")
        print("\nPlease ensure the Dataset folder from GitHub main branch is available.")
        print("\nYou can:")
        print("1. Clone the repository if not done")
        print("2. Pull the latest changes: git pull origin main")
        print("3. Ensure Dataset folder is in the repository root")
        return False
    
    print(f"✅ Dataset folder found at: {GITHUB_DATASET_PATH}")
    return True


def list_dataset_files():
    """List all files in the Dataset folder."""
    if not os.path.exists(GITHUB_DATASET_PATH):
        return []
    
    files = []
    for root, dirs, filenames in os.walk(GITHUB_DATASET_PATH):
        for filename in filenames:
            if filename.endswith(('.json', '.csv', '.xlsx', '.txt')):
                rel_path = os.path.relpath(os.path.join(root, filename), GITHUB_DATASET_PATH)
                files.append(rel_path)
    
    return files


def create_dataset_symlink():
    """Create symlink from local data folder to GitHub Dataset."""
    dataset_link = os.path.join(LOCAL_DATA_PATH, "dataset")
    
    # Remove existing symlink or directory
    if os.path.islink(dataset_link):
        os.unlink(dataset_link)
        print(f"Removed existing symlink: {dataset_link}")
    elif os.path.exists(dataset_link):
        print(f"⚠️  Directory exists: {dataset_link}")
        print("Please remove or rename it manually if you want to create a symlink.")
        return False
    
    # Create symlink
    try:
        os.symlink(GITHUB_DATASET_PATH, dataset_link)
        print(f"✅ Created symlink: {dataset_link} -> {GITHUB_DATASET_PATH}")
        return True
    except Exception as e:
        print(f"❌ Failed to create symlink: {e}")
        return False


def update_data_loader():
    """Update data loader to use GitHub dataset."""
    loader_path = os.path.join(LOCAL_DATA_PATH, "data_loader.py")
    
    loader_code = '''"""Data loader that uses GitHub Dataset folder.

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
        print("\\nFiles:")
        for file in info['files']:
            print(f"  - {file}")
'''
    
    with open(loader_path, 'w') as f:
        f.write(loader_code)
    
    print(f"✅ Created data loader: {loader_path}")


def generate_dataset_guide():
    """Generate a guide for using the GitHub dataset."""
    guide_path = os.path.join(LOCAL_DATA_PATH, "DATASET_USAGE.md")
    
    guide_content = """# Using GitHub Dataset

This guide explains how to use the Dataset folder from the GitHub repository instead of mock data.

## Setup

The system is now configured to use data from the GitHub Dataset folder.

### Dataset Location

```
/Users/utkarshsinha/Desktop/MSME360/Dataset/
```

This folder is linked to:

```
/Users/utkarshsinha/Desktop/MSME360/risk agent/data/dataset/
```

## Usage in Code

```python
from data.data_loader import load_from_dataset, get_dataset_info

# Load data file
data = load_from_dataset("your_file.json")

# Get dataset information
info = get_dataset_info()
print(f"Dataset has {info['file_count']} files")
```

## Fallback to Mock Data

If a file is not found in the Dataset folder, the system will automatically fall back to mock data with a warning.

## Available Data

Run this command to see what's available:

```bash
python data/data_loader.py
```

## Adding New Data

1. Add files to the Dataset folder in the GitHub repository
2. Pull the latest changes: `git pull origin main`
3. The new files will automatically be available

## Testing with Dataset

```bash
# Test with dataset file
curl -X POST http://localhost:8000/api/v1/evaluate \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer test_token" \\
  -d @data/dataset/your_file.json
```

## Troubleshooting

### Dataset folder not found

Ensure the Dataset folder exists in the repository root:

```bash
ls -la /Users/utkarshsinha/Desktop/MSME360/Dataset
```

### Symlink issues

If the symlink doesn't work, you can copy the dataset:

```bash
cp -r /Users/utkarshsinha/Desktop/MSME360/Dataset/* \\
      /Users/utkarshsinha/Desktop/MSME360/risk\\ agent/data/dataset/
```

### Permission issues

Ensure you have read permissions on the Dataset folder:

```bash
chmod -R +r /Users/utkarshsinha/Desktop/MSME360/Dataset
```
"""
    
    with open(guide_path, 'w') as f:
        f.write(guide_content)
    
    print(f"✅ Created dataset guide: {guide_path}")


def main():
    """Main function to set up GitHub dataset integration."""
    print("=" * 70)
    print("GitHub Dataset Integration Setup")
    print("=" * 70)
    print()
    
    # Check if dataset exists
    if not check_dataset_exists():
        print("\n⚠️  Setup incomplete. Dataset folder not found.")
        print("\nNext steps:")
        print("1. Ensure you've cloned the repository")
        print("2. Check that Dataset folder exists in repository root")
        print("3. Run this script again")
        return
    
    print()
    
    # List dataset files
    files = list_dataset_files()
    if files:
        print(f"📊 Found {len(files)} data files:")
        for f in files[:10]:  # Show first 10
            print(f"   - {f}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more")
    else:
        print("⚠️  No data files found in Dataset folder")
    
    print()
    
    # Create symlink
    print("Creating symlink to Dataset folder...")
    if create_dataset_symlink():
        print("✅ Symlink created successfully")
    else:
        print("⚠️  Could not create symlink (may need to copy manually)")
    
    print()
    
    # Create data loader
    print("Creating data loader module...")
    update_data_loader()
    
    print()
    
    # Generate guide
    print("Generating usage guide...")
    generate_dataset_guide()
    
    print()
    print("=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print()
    print("The system is now configured to use GitHub Dataset folder.")
    print()
    print("Test the setup:")
    print("  python data/data_loader.py")
    print()
    print("View the guide:")
    print("  cat data/DATASET_USAGE.md")


if __name__ == "__main__":
    main()

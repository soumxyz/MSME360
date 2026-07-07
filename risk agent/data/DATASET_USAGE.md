# Using GitHub Dataset

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
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
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
cp -r /Users/utkarshsinha/Desktop/MSME360/Dataset/* \
      /Users/utkarshsinha/Desktop/MSME360/risk\ agent/data/dataset/
```

### Permission issues

Ensure you have read permissions on the Dataset folder:

```bash
chmod -R +r /Users/utkarshsinha/Desktop/MSME360/Dataset
```

# Powershell script to run MSME alternate-data underwriting mock server on port 8080
$env:PYTHONPATH = "."
python -m uvicorn mock_server:app --host 127.0.0.1 --port 8080 --reload

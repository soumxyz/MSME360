import os
import urllib.request
import urllib.error
import mimetypes

def create_multipart_body(fields, files):
    boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    
    for name, value in fields.items():
        body.append(b'--' + boundary)
        body.append(f'Content-Disposition: form-data; name="{name}"'.encode('utf-8'))
        body.append(b'')
        body.append(value.encode('utf-8'))
        
    for name, filepath in files.items():
        if not filepath or not os.path.exists(filepath):
            continue
        filename = os.path.basename(filepath)
        mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        body.append(b'--' + boundary)
        body.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode('utf-8'))
        body.append(f'Content-Type: {mime_type}'.encode('utf-8'))
        body.append(b'')
        with open(filepath, 'rb') as f:
            body.append(f.read())
            
    body.append(b'--' + boundary + b'--')
    body.append(b'')
    return boundary, b'\r\n'.join(body)

def main():
    print("========================================================================")
    print("TESTING FASTAPI /VERIFY ENDPOINT VIA API CALL")
    print("========================================================================")

    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dataset")
    # Let's extract MSME002 this time to test another business
    bank_csv_path = os.path.join(dataset_dir, "bank_transactions.csv")
    gst_csv_path = os.path.join(dataset_dir, "gst_summary.csv")

    # Temp files for MSME002
    temp_bank = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_bank_msme002.csv")
    temp_gst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_gst_msme002.csv")

    try:
        # Extract MSME002 rows
        print("[INFO] Extracting statement rows for MSME002...")
        import csv
        with open(bank_csv_path, 'r', encoding='utf-8') as f_in, open(temp_bank, 'w', newline='', encoding='utf-8') as f_out:
            reader = csv.reader(f_in)
            writer = csv.writer(f_out)
            header = next(reader)
            writer.writerow(header)
            for row in reader:
                if row[1] == "MSME002": # Business_ID
                    writer.writerow(row)

        with open(gst_csv_path, 'r', encoding='utf-8') as f_in, open(temp_gst, 'w', newline='', encoding='utf-8') as f_out:
            reader = csv.reader(f_in)
            writer = csv.writer(f_out)
            header = next(reader)
            writer.writerow(header)
            for row in reader:
                if row[0] == "MSME002": # Business_ID
                    writer.writerow(row)

        # Build multipart body
        boundary, body_data = create_multipart_body(
            fields={},
            files={'bank_statement': temp_bank, 'gst_summary': temp_gst}
        )

        # Make request
        url = "http://127.0.0.1:8000/verify"
        req = urllib.request.Request(url, data=body_data)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary.decode("utf-8")}')
        
        print("[INFO] Sending POST request to FastAPI endpoint `/verify`...")
        with urllib.request.urlopen(req) as response:
            resp_code = response.getcode()
            resp_body = response.read().decode('utf-8')
            print(f"[SUCCESS] Response code: {resp_code}")
            print("Response JSON:")
            import json
            parsed = json.loads(resp_body)
            print(json.dumps(parsed, indent=2))
            
    except urllib.error.URLError as e:
        print(f"[FAIL] API request failed: {e}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
    finally:
        # Clean up temp files
        for temp_file in [temp_bank, temp_gst]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    main()

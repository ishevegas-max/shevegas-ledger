import os
import json
import urllib3
import pdfplumber
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
LEDGER_FILE = os.path.join(DATA_DIR, "civic_ledger.json")
DIRECTORY_FILE = os.path.join(DATA_DIR, "target_directory.json")

def initialize_directory():
    # If no directory exists, create a default structure to populate
    if not os.path.exists(DIRECTORY_FILE):
        default_targets = {
            "municipal_code_version": "2026-latest",
            "direct_pdf_urls": [
                # Drop your known Sheboygan packet or agenda URLs here
                "https://sheboygan-wi.municodemeetings.com/path/to/sample_packet.pdf"
            ],
            "local_ingest_folders": ["municipal_code"]
        }
        with open(DIRECTORY_FILE, "w") as f:
            json.dump(default_targets, f, indent=2)
        print("Initialized empty target_directory.json in data/")

def ingest_pdf_stream(pdf_path_or_url, source_name, is_url=True):
    print(f"Processing asset: {source_name}")
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    
    try:
        if is_url:
            headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
            response = http.request('GET', pdf_path_or_url, headers=headers, preload_content=False)
            if response.status != 200:
                print(f"Failed to fetch {source_name}. Status: {response.status}")
                return
            with open("temp.pdf", "wb") as f:
                for chunk in response.stream(32768):
                    f.write(chunk)
            target_path = "temp.pdf"
        else:
            target_path = pdf_path_or_url

        # Extract text matrices page by page
        extracted_content = []
        with pdfplumber.open(target_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    extracted_content.append({"page": i + 1, "text": text})

        # Save to main ledger storage
        history = []
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "r") as f:
                try: history = json.load(f)
                except: pass

        history.append({
            "timestamp_utc": datetime.utcnow().isoformat(),
            "source": source_name,
            "data_matrix": extracted_content
        })

        with open(LEDGER_FILE, "w") as f:
            json.dump(history, f, indent=2)
        print(f"Successfully committed {source_name} to ledger storage.")

        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")

    except Exception as e:
        print(f"Error ingesting {source_name}: {str(e)}")

def main():
    initialize_directory()
    
    with open(DIRECTORY_FILE, "r") as f:
        config = json.load(f)
    
    # 1. Process Direct PDF Link Directory
    for url in config.get("direct_pdf_urls", []):
        if "sample_packet.pdf" not in url:
            name = url.split("/")[-1]
            ingest_pdf_stream(url, name, is_url=True)

    # 2. Process Local Municipal Code Directory
    for folder in config.get("local_ingest_folders", []):
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith(".pdf"):
                    ingest_pdf_stream(os.path.join(folder, file), f"Municipal_Code_{file}", is_url=False)

if __name__ == '__main__':
    main()
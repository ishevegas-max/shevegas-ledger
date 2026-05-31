import os
import json
import pdfplumber
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import httpx

def get_httpx_client():
    # Use HTTP/2 with fallback retries to ensure better connection handling.
    return httpx.Client(http2=True) 

def get_request_session_with_proxy():
    # Define a requests session for robust retries and proxy routing.
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Optional to replace a list of endpoints fetching proxies.
    session.proxies = {
        "http": "http://free.public.proxy:8080",
        "https": "http://free.public.proxy:8080",
    }
    return session

def fetch_pdfs(base_url, pdf_dir):
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Assuming there's an API or specific URL structure for getting the PDFs
    # Example URL construction; adjust as necessary
    pdf_urls = ["https://sheboygan-wi.municodemeetings.com/some_pdf_path/example.pdf"]

    session = get_request_session_with_proxy()

    for url in pdf_urls:
        pdf_filename = url.split("/")[-1]
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        if not os.path.exists(pdf_path):
            response = session.get(url)
            if response.status_code == 200:
                with open(pdf_path, "wb") as f:
                    f.write(response.content)

def extract_pdf_data(pdf_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Example extraction, modify this logic as per the PDF structure
            data.append(page.extract_text())
    return data

def append_to_json(json_path, new_data):
    if not os.path.exists(json_path):
        with open(json_path, "w") as f:
            json.dump([], f)

    with open(json_path, "r") as f:
        data = json.load(f)

    data.extend(new_data)

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

def main():
    base_url = "https://sheboygan-wi.municodemeetings.com/"
    pdf_dir = "data/pdfs"
    json_path = "data/data.json"

    fetch_pdfs(base_url, pdf_dir)

    for pdf_file in os.listdir(pdf_dir):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        if pdf_path.endswith(".pdf"):
            extracted_data = extract_pdf_data(pdf_path)
            append_to_json(json_path, extracted_data)

if __name__ == "__main__":
    main()
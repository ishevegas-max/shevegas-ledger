import os
import json
import pdfplumber
import requests

def fetch_pdfs(base_url, pdf_dir):
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Assuming there's an API or specific URL structure for getting the PDFs
    # Example URL construction; adjust as necessary
    pdf_urls = ["https://sheboygan-wi.municodemeetings.com/some_pdf_path/example.pdf"]

    for url in pdf_urls:
        pdf_filename = url.split("/")[-1]
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        if not os.path.exists(pdf_path):
            response = requests.get(url)
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
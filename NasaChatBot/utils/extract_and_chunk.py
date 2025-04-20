import os
import fitz
from pathlib import Path

PDF_DIR = Path("D:/NasaChatBot/NasaChatBot/knowledge_base")
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_pdfs(path_dir):
    all_chunks = []

    for pdf_file in path_dir.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "content" : chunk,
                "source" : pdf_file.name,
                "chunk_id" : f"{pdf_file.stem}_chunk_{i}"
            })
    return all_chunks

if __name__ == "__main__":
    chunks = process_pdfs(PDF_DIR)
    print(f"Extracted {len(chunks)} total chunks.")
    import json
    with open("chunks.json", 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2)

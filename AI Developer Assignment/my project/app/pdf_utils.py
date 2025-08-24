import fitz  # PyMuPDF

def extract_text_chunks(pdf_path):
    doc = fitz.open(pdf_path)
    chunks = []
    for page in doc:
        text = page.get_text()
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for para in paragraphs:
            chunks.append(para)
    return chunks

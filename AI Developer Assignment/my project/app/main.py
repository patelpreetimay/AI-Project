from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.pdf_utils import extract_text_chunks
from app.embed_utils import generate_embeddings
from app.vector_db import VectorDB
from app.rag import answer_query
import os

app = FastAPI()
vector_db = VectorDB()
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_pdf/")
def upload_pdf(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    chunks = extract_text_chunks(filepath)
    embeddings = generate_embeddings(chunks)
    vector_db.add_documents(chunks, embeddings, file.filename)
    return {"status": "success", "chunks": len(chunks)}

@app.post("/query/")
def query_pdf(query: str = Form(...)):
    results = vector_db.search(query)
    answer, context = answer_query(query, results)
    return JSONResponse({"answer": answer, "context": context})

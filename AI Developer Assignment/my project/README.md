# PDF Q&A AI System

This project is a free, open-source AI-powered system that reads and understands PDF documents, and answers user queries based on their content. No paid APIs or billing are used; all models and libraries are open-source.

## Tech Stack
- Python
- FastAPI (backend API)
- sentence-transformers (embeddings)
- PyMuPDF (PDF parsing)
- FAISS (vector database)
- Streamlit (optional frontend)

## Features
- Upload multiple PDFs
- Extract and chunk text
- Generate embeddings (locally, free)
- Store embeddings in FAISS (local, free)
- Query answering using retrieval-augmented generation (RAG)
- Display answer, source PDF, and context

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Start Streamlit UI:
   ```bash
   streamlit run app/streamlit_ui.py
   ```

## Sample PDF
Place your sample PDFs in the `data/` folder.

## Known Issues

- Only local, free models are used (no OpenAI or paid APIs)
- Large PDFs may take time to process
- Answers may be basic: The system retrieves relevant text chunks and returns them using a simple template. It does not use a full language model for answer generation, so answers may lack deep reasoning or summarization.
- Context window for answers is limited by local model size
- PDF extraction quality depends on the source file (scanned/image-based PDFs may not work well)

## Troubleshooting & Improvements
- If answers are not appropriate, consider:
   - Ensuring PDFs are text-based and well-formatted
   - Tuning retrieval parameters in `vector_db.py`

## How it Works
1. Upload PDFs via API or Streamlit UI
2. Text is extracted and split into chunks
3. Chunks are embedded using sentence-transformers
4. Embeddings are stored in FAISS for fast search
5. When you ask a question, the system finds the most relevant chunks and returns them as context
6. The answer is generated using a simple template (not a full LLM)

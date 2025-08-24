import faiss
import numpy as np
from app.embed_utils import embed_query
import pickle
import os

class VectorDB:
    def __init__(self, index_path="data/faiss.index", meta_path="data/meta.pkl"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.chunks = []
        self.metadatas = []
        self.load()

    def add_documents(self, chunks, embeddings, pdf_name):
        # Ensure index is initialized
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))
        for i, chunk in enumerate(chunks):
            self.chunks.append(chunk)
            self.metadatas.append({"pdf": pdf_name, "chunk_id": len(self.chunks)-1})
        self.save()

    def search(self, query, top_k=5):
        q_emb = embed_query(query)
        D, I = self.index.search(np.array([q_emb]), top_k)
        results = [(self.chunks[i], self.metadatas[i]) for i in I[0]]
        return results

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump((self.chunks, self.metadatas), f)

    def load(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = None
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "rb") as f:
                self.chunks, self.metadatas = pickle.load(f)
        else:
            self.chunks, self.metadatas = [], []

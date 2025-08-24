def answer_query(query, results):
    # Simple RAG: concatenate top chunks as context
    context = "\n---\n".join([r[0] for r in results])
    # Use a local model for answer generation (placeholder)
    # For free, use a simple template or local LLM if available
    answer = f"Based on the documents, here's what I found:\n{context}"
    return answer, context

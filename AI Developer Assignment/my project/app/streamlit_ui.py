import streamlit as st
import requests

st.title("PDF Q&A AI System")

st.header("Upload PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    response = requests.post("http://localhost:8000/upload_pdf/", files=files)
    if response.ok:
        st.success(f"Uploaded {uploaded_file.name}. Chunks: {response.json()['chunks']}")
    else:
        st.error("Upload failed.")

st.header("Ask a Question")
query = st.text_input("Enter your question:")
if st.button("Submit Query") and query:
    response = requests.post("http://localhost:8000/query/", data={"query": query})
    if response.ok:
        st.write("**Answer:**", response.json()["answer"])
        st.write("**Context:**", response.json()["context"])
    else:
        st.error("Query failed.")

import os
import time
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pypdf

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "MODUL PEMBELAJARAN.pdf")
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

def extract_text_from_pdf(pdf_path):
    print(f"Mengekstrak teks dari {pdf_path}...")
    documents = []
    
    with open(pdf_path, "rb") as file:
        pdf = pypdf.PdfReader(file)
        for i, page in enumerate(pdf.pages):
            import re
            text = page.extract_text()
            if text:
                # Bersihkan newline yang berlebihan agar LLM tidak kebingungan membaca teks yang terputus-putus
                text = re.sub(r'\s+', ' ', text).strip()
            
            # Nilai Tambah N6: Jika teks sangat sedikit (kemungkinan besar itu adalah screenshot penuh),
            # kita bisa menandainya atau menyimpannya. Untuk prototipe awal, kita andalkan pypdf.
            if text and len(text) > 50:
                documents.append({
                    "text": text,
                    "metadata": {"page": i + 1, "source": pdf_path}
                })
    return documents

def main():
    # 1. Ekstrak Teks
    docs = extract_text_from_pdf(DATA_PATH)
    print(f"Berhasil mengekstrak {len(docs)} halaman.")

    # 2. Chunking
    print("Memecah teks (chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunked_docs = []
    chunked_metadatas = []
    
    for doc in docs:
        chunks = text_splitter.split_text(doc["text"])
        for chunk in chunks:
            chunked_docs.append(chunk)
            chunked_metadatas.append(doc["metadata"])
            
    print(f"Total chunks dibuat: {len(chunked_docs)}")

    # 3. Embedding & Indexing
    print("Membuat embedding dan menyimpan ke Vector Store (Chroma)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    vectorstore = Chroma.from_texts(
        texts=chunked_docs,
        metadatas=chunked_metadatas,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print("Proses Ingestion selesai! Database tersimpan di:", DB_DIR)

if __name__ == "__main__":
    main()

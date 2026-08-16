import os
import time
import fitz  # PyMuPDF
from PIL import Image
import io
import json
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "MODUL PEMBELAJARAN.pdf")
DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# Setup Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Menggunakan Gemini Flash Lite yang limit gratisnya jauh lebih besar (1500 per hari)
vision_model = genai.GenerativeModel("gemini-3.5-flash-lite")

def extract_text_and_images_with_vlm(pdf_path):
    cache_path = os.path.join(BASE_DIR, "data", "vlm_cache.json")
    if os.path.exists(cache_path):
        print("Membaca hasil OCR dari cache (vlm_cache.json) agar tidak mengulang 5 menit...")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Mulai memproses {pdf_path} dengan Gemini Vision OCR...")
    documents = []
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    for i in range(total_pages):
        print(f"Memproses Halaman {i + 1}/{total_pages}...")
        page = doc.load_page(i)
        
        # Render halaman menjadi gambar resolusi tinggi
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Prompt untuk VLM
        prompt = """Anda adalah asisten AI ekstraktor dokumen profesional.
Tugas Anda adalah membaca gambar halaman PDF ini dan mengekstrak SELURUH teks yang ada di dalamnya dengan sempurna.
Jika terdapat gambar ilustrasi, screenshot aplikasi, atau tabel, deskripsikan isi gambar tersebut sedetail mungkin dalam kurung siku, misalnya: [Gambar: Screenshot menu X dengan tombol Y].
Jangan merangkum teks aslinya, tuliskan persis seperti apa adanya, namun Anda boleh merapikan format paragrafnya agar mudah dibaca.
Keluarkan output HANYA teks ekstraksinya saja, tanpa pengantar atau penutup."""
        
        try:
            # Panggil Gemini Vision API
            response = vision_model.generate_content([prompt, img])
            text = response.text
            
            if text and len(text.strip()) > 10:
                documents.append({
                    "text": text,
                    "metadata": {"page": i + 1, "source": pdf_path}
                })
        except Exception as e:
            print(f"Error pada halaman {i+1}: {e}")
            
        # Penanganan Rate Limit (15 Requests Per Minute untuk Free Tier)
        # 60 detik / 15 request = 4 detik per request (kita gunakan 5 detik agar aman)
        time.sleep(5)
        
    # Simpan hasil ke cache agar tidak hilang jika embedding gagal
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
        
    return documents

def main():
    print("=== MULTIMODAL VLM INGESTION ===")
    print("Peringatan: Proses ini akan memakan waktu ~5 menit karena API Rate Limit.")
    
    docs = extract_text_and_images_with_vlm(DATA_PATH)
    print(f"\nBerhasil mengekstrak {len(docs)} halaman menggunakan Gemini Vision.")

    print("Memecah teks (chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
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
            
    print(f"Total chunks VLM dibuat: {len(chunked_docs)}")

    print("Membuat embedding dan menyimpan ke Vector Store (Chroma) secara bertahap...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    # Inisialisasi Chroma
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    # Batasi batch size menjadi 80 (karena limit API gratis Gemini adalah 100 teks per menit)
    batch_size = 80
    for i in range(0, len(chunked_docs), batch_size):
        end_idx = min(i + batch_size, len(chunked_docs))
        print(f"Memproses embedding chunk {i+1} hingga {end_idx} dari {len(chunked_docs)}...")
        
        batch_texts = chunked_docs[i:end_idx]
        batch_metas = chunked_metadatas[i:end_idx]
        
        vectorstore.add_texts(texts=batch_texts, metadatas=batch_metas)
        
        if end_idx < len(chunked_docs):
            print("Mencapai batas aman API. Menunggu 60 detik untuk mereset kuota (Rate Limit) Gemini...")
            time.sleep(60)
    
    
    print("Proses VLM Ingestion selesai! Database telah diperbarui di:", DB_DIR)

if __name__ == "__main__":
    main()

# Spesifikasi Desain: Chatbot RAG "Accurate Online"

**Tanggal:** 2026-08-13
**Konteks:** Take-Home Test Junior AI Engineer 2026

## 1. Tujuan Sistem
Membangun prototipe Chatbot RAG (Retrieval-Augmented Generation) berbasis Python yang mampu menjawab pertanyaan terkait *Accurate Online* berdasarkan dokumen modul 64 halaman, lengkap dengan kemampuan menangani memori percakapan, kejujuran (menolak menjawab di luar konteks), serta mengimplementasikan semua "Nilai Tambah" (Hybrid Search, OCR, Observability, Evaluasi RAGAS, efisiensi metrik, dan *cloud deployment*).

## 2. Arsitektur Komponen

### A. Ingestion & Pengindeksan (Data Pipeline)
*   **Ekstraksi Teks & Gambar**: `PyMuPDF` (fitz) untuk ekstraksi teks dari PDF. Mengingat modul berisi banyak tangkapan layar, teks dalam gambar akan diekstrak menggunakan metode OCR (Tesseract atau LLM Vision) untuk mengoptimalkan pencarian data berbentuk tabel/gambar (Memenuhi **N6**).
*   **Strategi Chunking**: Menggunakan `RecursiveCharacterTextSplitter`. Ukuran *chunk* di kisaran 500-1000 karakter dengan *overlap* 100-200 karakter. Metadata nomor halaman akan disisipkan di setiap *chunk* untuk referensi sumber.
*   **Vector Store & Embeddings**: Menggunakan `ChromaDB` sebagai penyimpanan lokal yang ringan, dikombinasikan dengan `GoogleGenerativeAIEmbeddings` untuk konversi teks ke vektor.

### B. Mekanisme Retrieval (Pencarian Data)
*   **Hybrid Search (N2)**: Penggabungan *Dense Retrieval* (pencarian vektor/semantik) dan *Sparse Retrieval* (pencarian leksikal menggunakan **BM25**). BM25 bertugas memastikan kata kunci spesifik (seperti "Faktur Pembelian") tidak terlewatkan oleh pencarian vektor.
*   **Reranking**: Hasil gabungan dari Dense dan BM25 akan diurutkan ulang (*rerank*) menggunakan model *Cross-Encoder* ringan atau Cohere (jika API tersedia) untuk memilih 3-5 konteks teratas (*Top-K*).

### C. LLM & Generasi Jawaban
*   **LLM Provider**: Menggunakan **Google Gemini Pro** (via API gratis) sebagai mesin utama. Diimplementasikan mekanisme *fallback* ke **Groq** (model Llama-3/Mixtral) apabila Gemini mengalami *rate limit* atau gangguan.
*   **Prompt Engineering**: *System Prompt* akan secara eksplisit memaksa LLM untuk:
    1. Hanya menjawab menggunakan konteks yang diberikan.
    2. Jika konteks tidak relevan dengan pertanyaan, menolak menjawab dengan sopan (Memenuhi **W4**).
    3. Menyertakan referensi sumber dokumen (Memenuhi **W2**).
*   **Memori Percakapan**: Menggunakan pola *Contextualizing the Question*. Riwayat percakapan sebelumnya dan pertanyaan baru akan dikirim ke LLM untuk dirumuskan ulang menjadi satu pertanyaan mandiri (*standalone query*) sebelum dilakukan *retrieval*. Ini mengatasi ambiguitas rujukan implisit (Memenuhi **W3**).

### D. Observability & Metrik (N3 & N4)
*   **Langfuse / LangSmith**: Terintegrasi pada level *chain* LangChain untuk mencatat seluruh jejak eksekusi (waktu, *latency*, tahap pencarian, *prompt* yang dihasilkan).
*   **Penghitungan Token**: Sistem akan mencatat estimasi penggunaan token dan biaya untuk setiap pertanyaan, dan menampilkannya kepada pengguna (Memenuhi **N4**).

### E. Evaluasi Terukur (N1)
*   Skrip mandiri menggunakan kerangka **RAGAS** akan disediakan. Skrip ini akan berisi 10-20 dataset pertanyaan-jawaban emas (*golden dataset*), lalu secara otomatis menilai performa prototipe berdasarkan metrik *Faithfulness*, *Answer Relevance*, dan *Context Precision*.

### F. Antarmuka Pengguna & Deployment (N5)
*   **UI**: Dibangun menggunakan **Streamlit**, menampilkan antarmuka *chat* yang responsif.
*   **Deployment**: Kode dirancang untuk di-*deploy* langsung dari repositori GitHub ke **Streamlit Cloud** (gratis, tanpa perlu instalasi server), memungkinkan penilai mengakses *chatbot* secara langsung (Memenuhi **N5**).

## 3. Rencana Tahapan Eksekusi (Implementation Plan)
1. **Setup & Lingkungan**: Inisiasi *virtual environment*, instalasi *dependencies* (LangChain, Streamlit, PyMuPDF, ChromaDB, dll), dan setup *API Keys* (.env).
2. **Ingestion Script**: Membuat skrip untuk memproses PDF, OCR, melakukan *chunking*, dan menyimpan vektor ke disk.
3. **Retrieval Module**: Membangun mekanisme *Hybrid Search* (Vector + BM25) dan *Reranker*.
4. **Chatbot Backend**: Mengintegrasikan LLM (Gemini + Groq Fallback), mekanisme memori (*contextualize query*), dan observabilitas (*Langfuse/LangSmith*).
5. **Streamlit UI**: Menggabungkan *backend* dengan *frontend*, menambah UI untuk menampilkan sumber dokumen, *latency*, dan *token usage*.
6. **Dokumentasi & Skrip Evaluasi**: Menulis README yang komprehensif, mencatat *trade-off* teknis, serta membangun skrip evaluasi RAGAS.

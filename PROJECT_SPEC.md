# Project Specification: Accurate Online RAG Chatbot

**Version:** 1.0
**Date:** 2026-08-20
**Project Context:** Take-Home Test - Junior AI Engineer 2026

## 1. Executive Summary
Proyek ini adalah prototipe aplikasi Chatbot berbasis RAG (*Retrieval-Augmented Generation*) yang dirancang khusus untuk menjawab pertanyaan berdasarkan dokumen "Modul Pembelajaran Accurate Online" (64 halaman). Sistem ini dibangun menggunakan ekosistem Python modern dan mendemonstrasikan implementasi *Super-Hybrid RAG* untuk memaksimalkan akurasi penarikan informasi dari bahasa Indonesia.

## 2. Core Requirements (Wajib)
Sistem ini memenuhi seluruh kriteria wajib berikut:
- **W1 (RAG Implementation):** Sistem hanya mencari jawaban dan konteks dari PDF modul pembelajaran yang disediakan.
- **W2 (Source Citation):** Chatbot selalu menyertakan nomor halaman PDF sebagai referensi atas jawabannya.
- **W3 (Conversational Memory):** Chatbot mampu mengingat konteks dari obrolan sebelumnya untuk menjawab pertanyaan yang merujuk pada pesan terdahulu (contoh: "Apa bedanya yang pertama dan kedua?").
- **W4 (Guardrails/Honesty):** Jika informasi tidak ditemukan dalam dokumen (contoh: pertanyaan harga langganan atau fitur fiktif), model dengan sopan menolak menjawab dan tidak berhalusinasi.
- **W5 & W6 (Tech Stack):** Menggunakan framework **Python**, **LangChain**, dan **Streamlit**.

## 3. Advanced Features (Nilai Tambah)
- **N1 (Evaluation Script):** Tersedia skrip terpisah (`src/evaluate.py`) menggunakan framework **RAGAS** untuk mengukur skor faktualitas (*Faithfulness*) dan relevansi jawaban.
- **N2 (Hybrid Search):** Penggabungan *Semantic Search* (vektor) dan *Lexical Search* (BM25 keyword) secara paralel untuk menghindari kehilangan konteks krusial bahasa Indonesia.
- **N3 (Observability):** Penggunaan **LangSmith** di belakang layar untuk melacak setiap tahapan RAG (*trace latency*, evaluasi *chunk*, *prompt generation*).
- **N4 (Metrics UI):** Menampilkan estimasi waktu pemrosesan (*latency*) dan perhitungan konsumsi *Token* secara *real-time* di antarmuka Streamlit.
- **N5 (Cloud Deployment):** Aplikasi sudah berhasil di-*deploy* ke **Streamlit Cloud** sehingga dapat diakses secara instan tanpa proses instalasi lokal.
- **N6 (Multimodal OCR):** Pipeline injeksi data (`src/ingest_vlm.py`) memanfaatkan Gemini Vision VLM untuk mengekstrak dan mendeskripsikan tabel/gambar dari modul PDF menjadi *chunk* teks yang terindeks.

## 4. Architecture & Tech Stack

### A. Data Ingestion & Indexing Pipeline
- **PDF Parser:** `PyMuPDF` (fitz) untuk ekstraksi teks berkecepatan tinggi.
- **Vision/OCR LLM:** `Google Gemini Pro Vision` untuk menerjemahkan tangkapan layar antarmuka Accurate Online dan tabel menjadi teks.
- **Chunking Strategy:** `RecursiveCharacterTextSplitter` (1000 karakter, overlap 200). Metadata nomor halaman disisipkan dalam setiap *chunk*.
- **Embedding Model:** `Google Generative AI Embeddings` (`models/gemini-embedding-2`).
- **Vector Database:** `ChromaDB` (penyimpanan lokal persisten di folder `./chroma_db`).

### B. Retrieval Module (Super-Hybrid RAG)
- **Lexical Retriever:** `BM25Retriever` (Sparse search).
- **Semantic Retriever:** ChromaDB Vector Store Retriever (Dense search).
- **Ensemble Retriever:** Menggabungkan hasil BM25 dan ChromaDB dengan rasio optimal (contoh: 50/50).
- **Note on Reranker:** Modul *Reranking* (seperti Flashrank) **dihilangkan** dari *pipeline* akhir karena pada teks bahasa Indonesia, metode ini seringkali secara keliru membuang *chunk* relevan yang dihasilkan oleh BM25, sehingga Super-Hybrid BM25+Chroma terbukti menjadi konfigurasi paling stabil.

### C. LLM Engine & Generation
- **Primary LLM:** `GPT OSS 120B` via **Groq** (`openai/gpt-oss-120b`). Dipilih karena kecepatannya yang superior dan parameter raksasanya menghasilkan logika berbahasa Indonesia yang sangat presisi setara GPT-4.
- **Fallback LLM:** `Gemini 1.5 Flash` digunakan apabila koneksi ke API Groq gagal atau terkena batas akses (*rate limit*).
- **History-Aware Strategy:** Setiap kueri pengguna yang memiliki riwayat percakapan akan diformulasikan ulang (*Contextualized*) menjadi *standalone query* sebelum dilakukan pencarian dokumen.

### D. User Interface (Frontend)
- **Framework:** `Streamlit`.
- **PDF Viewer Optimization:** Penampil PDF dirancang kustom menggunakan `PyMuPDF` untuk merender halaman langsung ke memori (*image bytes*). Seluruh proses navigasi halaman dibungkus dalam `@st.fragment` untuk mencegah *full-page reload* dan menjaga pengalaman pengguna (UX) semulus *Single Page Application* (SPA).

## 5. Security & Environment
- File `.env` digunakan untuk manajemen kunci (Groq API, Google API, LangChain API).
- Kunci API diatur sebagai variabel *Secrets* secara aman di *dashboard* konfigurasi Streamlit Cloud.
- Kode tidak menyimpan kredensial secara *hardcode*.

---
*Dokumen ini merupakan spesifikasi teknis final yang merefleksikan seluruh pembaruan pada iterasi rilis terbaru (termasuk migrasi model ke GPT OSS 120B).*

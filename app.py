import streamlit as st
import time
import re
import os
import fitz # PyMuPDF
from src.rag_pipeline import setup_rag_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler

# --- Custom Token Tracker ---
class TokenTracker(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0
        
    def on_llm_end(self, response, **kwargs):
        try:
            generation = response.generations[0][0]
            if hasattr(generation, "message") and hasattr(generation.message, "usage_metadata"):
                usage = generation.message.usage_metadata
                if usage:
                    self.total_tokens += usage.get("total_tokens", 0)
        except Exception:
            pass

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Chatbot Accurate Online", page_icon="🤖", layout="wide")

# Custom CSS agresif untuk membunuh scrollbar utama
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .stApp {
        overflow: hidden !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.subheader("🤖 Chatbot RAG - Accurate Online")

# --- Inisialisasi Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "rag_chain" not in st.session_state:
    try:
        st.session_state.rag_chain = setup_rag_chain()
        st.success("Berhasil memuat model dan database! Siap digunakan.")
    except Exception as e:
        st.error(f"Gagal memuat RAG pipeline: {e}")
if "metrics" not in st.session_state:
    st.session_state.metrics = {"total_latency": 0, "queries": 0, "total_tokens": 0}
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "demo_index" not in st.session_state:
    st.session_state.demo_index = -1

# Fungsi cache super cepat untuk PDF
@st.cache_data
def get_pdf_total_pages(pdf_path):
    doc = fitz.open(pdf_path)
    return len(doc)

@st.cache_data(max_entries=100)
def get_pdf_page_image(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)
    # dpi=100 sangat ringan (hanya beberapa puluh KB) jadi loading gambar instan!
    pix = page.get_pixmap(dpi=100)
    return pix.tobytes()

# --- Sidebar ---
with st.sidebar:
    st.header("Metrik Sistem 📊")
    if st.session_state.metrics["queries"] > 0:
        avg_latency = st.session_state.metrics["total_latency"] / st.session_state.metrics["queries"]
        st.metric("Rata-rata Latency", f"{avg_latency:.2f} s")
    else:
        st.metric("Rata-rata Latency", "0.00 s")
    st.metric("Total Pertanyaan", st.session_state.metrics["queries"])
    
    st.markdown("---")
    st.subheader("Estimasi Biaya 💰")
    st.metric("Token Digunakan", f"{st.session_state.metrics['total_tokens']:,}")
    # Asumsi harga Groq Llama-3 70B: ~Rp 15 per 1000 token
    cost_rp = (st.session_state.metrics['total_tokens'] / 1000) * 15
    st.metric("Estimasi Harga", f"Rp {cost_rp:,.2f}")
    
    st.markdown("---")
    if st.button("Hapus Riwayat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_page = 1
        st.rerun()

    st.markdown("---")
    st.header("Demo Rekruter 🎯")
    st.info("Simulasi otomatis menjawab 7 pertanyaan teknis wajib dari file Take-Home Test.")
    if st.button("▶️ Jalankan Demo Tes", type="primary", use_container_width=True):
        st.session_state.demo_index = 0
        st.rerun()

# --- Layout Dua Kolom ---
chat_col, pdf_col = st.columns([1, 1])
pdf_container = pdf_col.empty()

with chat_col:
    st.subheader("💬 Chat Room")
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.chat_history:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)
                    
                    # Tampilkan ulang referensi jika ada di dalam memory
                    if "context" in message.additional_kwargs:
                        with st.expander("🔍 Lihat Referensi Dokumen Asli"):
                            for i, doc in enumerate(message.additional_kwargs["context"]):
                                st.markdown(f"**Referensi {i+1} (Halaman {doc['page']})**")
                                st.info(doc['content'])
        processing_container = st.empty()
                    
    user_query = st.chat_input("Tanyakan sesuatu tentang Accurate Online...")
    if user_query:
        with processing_container.container():
            with st.chat_message("user"):
                st.write(user_query)
            st.session_state.chat_history.append(HumanMessage(content=user_query))
            
            with st.chat_message("assistant"):
                with st.spinner("Mencari di modul pembelajaran..."):
                    start_time = time.time()
                    try:
                        
                        tracker = TokenTracker()
                        response = st.session_state.rag_chain.invoke(
                            {
                                "input": user_query,
                                "chat_history": st.session_state.chat_history[:-1] 
                            },
                            config={"callbacks": [tracker]}
                        )
                        answer = response.get("answer", "Maaf, saya tidak dapat merumuskan jawaban.")
                        st.write(answer)
                        
                        
                        # Simpan token
                        st.session_state.metrics["total_tokens"] += tracker.total_tokens
                        
                        # Buat AIMessage
                        ai_message = AIMessage(content=answer)
                        
                        # Tampilkan Referensi Konteks (Debug Mode N3)
                        context_docs = response.get("context", [])
                        if context_docs:
                            ai_message.additional_kwargs["context"] = [
                                {"page": d.metadata.get("page", "?"), "content": d.page_content}
                                for d in context_docs
                            ]
                            with st.expander("🔍 Lihat Referensi Dokumen Asli"):
                                st.markdown("*Konteks di bawah ini ditarik secara otomatis oleh sistem pencarian Super-Hybrid (Vector ChromaDB + BM25).*")
                                for i, doc in enumerate(context_docs):
                                    hal = doc.metadata.get("page", "Tidak diketahui")
                                    st.markdown(f"**Referensi {i+1} (Halaman {hal})**")
                                    st.info(doc.page_content)
                        
                        st.session_state.chat_history.append(ai_message)
                        
                        page_changed = False
                        match = re.search(r'Halaman\s+(\d+)', answer, re.IGNORECASE)
                        if match:
                            new_page = int(match.group(1))
                            if new_page != st.session_state.current_page:
                                st.session_state.current_page = new_page
                                page_changed = True
                            
                        end_time = time.time()
                        st.session_state.metrics["total_latency"] += (end_time - start_time)
                        st.session_state.metrics["queries"] += 1
                        
                        # Hanya rerun jika halamannya berubah agar tidak boros proses
                        if page_changed:
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {str(e)}")
                        st.session_state.chat_history.pop()

    # Eksekusi Demo Otomatis (Per Pertanyaan agar UI bisa Update)
    if st.session_state.get("demo_index", -1) >= 0:
        idx = st.session_state.demo_index
        from src.evaluate import questions
        
        if idx < len(questions):
            q = questions[idx]
            with processing_container.container():
                with st.chat_message("user"):
                    st.write(q)
                st.session_state.chat_history.append(HumanMessage(content=q))
                
                with st.chat_message("assistant"):
                    with st.spinner(f"Menjawab pertanyaan {idx+1}/{len(questions)}..."):
                        start_time = time.time()
                        try:
                            tracker = TokenTracker()
                            response = st.session_state.rag_chain.invoke(
                                {"input": q, "chat_history": []},
                                config={"callbacks": [tracker]}
                            )
                            answer = response.get("answer", "Maaf, terjadi kesalahan.")
                            st.write(answer)
                            
                            st.session_state.metrics["total_tokens"] += tracker.total_tokens
                            
                            ai_message = AIMessage(content=answer)
                            
                            # Tampilkan Referensi Konteks (Debug Mode N3)
                            context_docs = response.get("context", [])
                            if context_docs:
                                ai_message.additional_kwargs["context"] = [
                                    {"page": d.metadata.get("page", "?"), "content": d.page_content}
                                    for d in context_docs
                                ]
                                with st.expander("🔍 Lihat Referensi Dokumen Asli"):
                                    for i, doc in enumerate(context_docs):
                                        st.markdown(f"**Referensi {i+1} (Halaman {doc.metadata.get('page', '?')})**")
                                        st.info(doc.page_content)
                                        
                            st.session_state.chat_history.append(ai_message)
                            
                            # Ekstrak halaman agar PDF ikut pindah
                            match = re.search(r'Halaman\s+(\d+)', answer, re.IGNORECASE)
                            if match:
                                st.session_state.current_page = int(match.group(1))
                            
                            # Update metrik
                            end_time = time.time()
                            st.session_state.metrics["total_latency"] += (end_time - start_time)
                            st.session_state.metrics["queries"] += 1
                        except Exception as e:
                            st.error(f"Gagal: {e}")
            
            # Tandai bahwa demo baru saja dijawab, agar kita bisa sleep & rerun di bawah
            st.session_state.demo_index += 1
            st.session_state.demo_just_processed = True
        else:
            # Demo selesai
            st.session_state.demo_index = -1
            st.success("🎉 Demo 7 Pertanyaan Selesai!")

# --- Render PDF Viewer (Super Cepat dengan Cache) ---
@st.fragment
def show_pdf_viewer(pdf_path):
    total_pages = get_pdf_total_pages(pdf_path)
    if st.session_state.current_page < 1:
        st.session_state.current_page = 1
    elif st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
    
    pdf_view_container = st.container(height=500)
    with pdf_view_container:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 3])
        with col2:
            st.number_input("Halaman", min_value=1, max_value=total_pages, key="current_page", step=1, label_visibility="collapsed")
        with col3:
            st.markdown(f"<div style='text-align: left; padding-top: 5px; font-weight: bold;'>/ {total_pages}</div>", unsafe_allow_html=True)
                
        img_bytes = get_pdf_page_image(pdf_path, st.session_state.current_page)
        st.image(img_bytes, use_column_width=True)

with pdf_container.container():
    st.subheader("📄 Modul Pembelajaran")
    pdf_path = os.path.join(os.path.dirname(__file__), "data", "MODUL PEMBELAJARAN.pdf")
    if os.path.exists(pdf_path):
        try:
            show_pdf_viewer(pdf_path)
        except Exception as e:
            st.error(f"Gagal merender halaman PDF: {str(e)}")
    else:
        st.warning("File Modul PDF tidak ditemukan.")

# --- Demo Auto-Scroll Handler ---
# Berjalan di paling bawah agar PDF Viewer sempat ter-render dengan halaman baru!
if st.session_state.get("demo_just_processed", False):
    st.session_state.demo_just_processed = False
    time.sleep(4)
    st.rerun()

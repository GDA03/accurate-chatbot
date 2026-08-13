import streamlit as st
import time
from src.rag_pipeline import setup_rag_chain
from langchain_core.messages import HumanMessage, AIMessage

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Chatbot Accurate Online", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot RAG - Accurate Online")
st.markdown("Prototipe asisten cerdas untuk menjawab pertanyaan seputar *Accurate Online*.")

# --- Inisialisasi Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "rag_chain" not in st.session_state:
    # Memuat rag_chain hanya sekali
    try:
        st.session_state.rag_chain = setup_rag_chain()
        st.success("Berhasil memuat model dan database! Siap digunakan.")
    except Exception as e:
        st.error(f"Gagal memuat RAG pipeline: {e}")

if "metrics" not in st.session_state:
    st.session_state.metrics = {"total_latency": 0, "queries": 0}

# --- Sidebar untuk Metrik & Observability (N3 & N4) ---
with st.sidebar:
    st.header("Metrik Sistem 📊")
    st.write("Catatan performa dan efisiensi:")
    if st.session_state.metrics["queries"] > 0:
        avg_latency = st.session_state.metrics["total_latency"] / st.session_state.metrics["queries"]
        st.metric("Rata-rata Latency", f"{avg_latency:.2f} s")
    else:
        st.metric("Rata-rata Latency", "0.00 s")
        
    st.metric("Total Pertanyaan", st.session_state.metrics["queries"])
    st.markdown("---")
    st.markdown("**Observabilitas**: Terhubung ke LangSmith (jika `LANGCHAIN_API_KEY` aktif di `.env`).")
    st.markdown("**Hybrid Search**: Menggunakan *BM25* + *Dense Retrieval* (jika diaktifkan di backend).")
    
    if st.button("Hapus Riwayat"):
        st.session_state.chat_history = []
        st.rerun()

# --- Fungsi Menampilkan Chat ---
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# --- Input Pengguna ---
user_query = st.chat_input("Tanyakan sesuatu tentang Accurate Online...")

if user_query:
    # 1. Tampilkan pertanyaan user
    with st.chat_message("user"):
        st.write(user_query)
    
    # 2. Tambahkan ke history
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    # 3. Proses Jawaban dengan Spinner
    with st.chat_message("assistant"):
        with st.spinner("Mencari di modul pembelajaran..."):
            start_time = time.time()
            
            try:
                # Memanggil RAG Chain
                response = st.session_state.rag_chain.invoke({
                    "input": user_query,
                    # HANYA kirim riwayat masa lalu (tanpa pertanyaan saat ini) agar model memori tidak bingung
                    "chat_history": st.session_state.chat_history[:-1] 
                })
                
                answer = response.get("answer", "Maaf, saya tidak dapat merumuskan jawaban.")
                st.write(answer)
                
                # Menambahkan jawaban AI ke history
                st.session_state.chat_history.append(AIMessage(content=answer))
                
                # Update Metrics
                end_time = time.time()
                latency = end_time - start_time
                st.session_state.metrics["total_latency"] += latency
                st.session_state.metrics["queries"] += 1
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
                # Pop the user message from history if error
                st.session_state.chat_history.pop()

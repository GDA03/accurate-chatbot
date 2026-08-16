import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict, Any
from langchain.schema import Document

# Load Env
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
DATA_PATH = os.path.join(BASE_DIR, "data", "MODUL PEMBELAJARAN.pdf")

# ==========================================
# 1. HYBRID RETRIEVER (N2)
# ==========================================
class HybridRetriever:
    """
    Kustomisasi Retriever yang menggabungkan Semantic Search (Dense/Chroma) 
    dan Keyword Search (Sparse/BM25) untuk akurasi maksimal.
    """
    def __init__(self, vectorstore: Any, documents: List[Document]):
        self.vectorstore = vectorstore
        self.documents = documents
        
        # Inisialisasi BM25 (Sparse)
        tokenized_corpus = [doc.page_content.split(" ") for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
    def get_relevant_documents(self, query: str, top_k: int = 5) -> List[Document]:
        """Menggabungkan hasil Dense dan Sparse lalu menghilangkan duplikat."""
        # 1. Vector Search (Dense)
        dense_docs = self.vectorstore.similarity_search_with_score(query, k=top_k)
        
        # 2. BM25 Search (Sparse)
        tokenized_query = query.split(" ")
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_n_bm25 = np.argsort(bm25_scores)[::-1][:top_k]
        sparse_docs = [(self.documents[i], bm25_scores[i]) for i in top_n_bm25 if bm25_scores[i] > 0]
        
        # 3. Gabungkan dan hapus duplikat (Reranking sederhana berdasarkan frekuensi kemunculan)
        combined_docs = {}
        
        for doc, score in dense_docs:
            combined_docs[doc.page_content] = doc
            
        for doc, score in sparse_docs:
            if doc.page_content not in combined_docs:
                combined_docs[doc.page_content] = doc
                
        # Return list of unique documents
        return list(combined_docs.values())[:top_k]

# ==========================================
# 2. SETUP RAG PIPELINE
# ==========================================
def get_llm() -> Any:
    """Menggunakan Groq (Llama-3.1 8B) sebagai LLM utama karena lebih stabil dan cepat."""
    try:
        # Menggunakan Llama-3.3 70B via Groq untuk kualitas setara GPT-4
        return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2)
    except Exception:
        # Fallback ke Gemini jika Groq gagal/tidak ada API key
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

def setup_rag_chain() -> Any:
    """
    Menginisialisasi seluruh rantai RAG (Retrieval-Augmented Generation).
    Proses ini mencakup:
    1. Memuat ChromaDB dan menyiapkan Ensemble Hybrid Retriever.
    2. Membuat History-Aware Retriever untuk mempertahankan konteks chat.
    3. Merangkai sistem Prompt dengan Guardrail super ketat.
    """
    # 1. Load Vector Store (Dense Search)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    # Ambil semua dokumen dari Chroma untuk BM25
    all_data = vectorstore.get()
    all_docs = [Document(page_content=txt, metadata=meta) for txt, meta in zip(all_data['documents'], all_data['metadatas'])]
    
    # Setup BM25 (Sparse Search)
    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = 3
    
    # Setup Chroma Retriever
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Gabungkan Keduanya (Hybrid Search N2)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5]
    )
    
    # Tambahkan Flashrank Reranker (N2)
    from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
    from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
    
    compressor = FlashrankRerank()
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=ensemble_retriever
    )
    
    llm = get_llm()
    
    # 2. Contextualize Question (Memori - W3)
    contextualize_q_system_prompt = """Diberikan riwayat percakapan dan pertanyaan terbaru dari pengguna, \
rumuskan ulang pertanyaan tersebut menjadi pertanyaan mandiri tanpa mengubah maknanya. \
Jangan menjawab pertanyaan, cukup rumuskan ulang."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, compression_retriever, contextualize_q_prompt
    )
    
    # 3. RAG System Prompt (Kejujuran - W4 & W2 & Komunikatif)
    qa_system_prompt = """Anda adalah asisten AI yang ramah, komunikatif, dan interaktif khusus untuk software Accurate Online.
Tugas Anda adalah memandu pengguna dan menjawab pertanyaan HANYA berdasarkan informasi dari KONTEKS di bawah ini.

KONTEKS:
{context}

ATURAN SANGAT KETAT:
1. PENOLAKAN TOPIK DI LUAR DOMAIN (HARD GUARDRAIL): Jika pengguna menanyakan topik yang SAMA SEKALI TIDAK RELEVAN dengan Accurate Online, Akuntansi, atau sistem bisnis (contoh: pertanyaan tentang politik, tokoh seperti Prabowo, bahasa pemrograman seperti Javascript, resep masakan, dll), Anda WAJIB langsung menolak menjawab. Katakan dengan sopan bahwa Anda adalah asisten khusus Accurate Online dan tidak diprogram untuk menjawab topik tersebut. JANGAN PERNAH menggunakan pengetahuan umum Anda untuk menjawabnya.
2. JAWAB HANYA DARI KONTEKS: Untuk pertanyaan seputar Accurate Online/Akuntansi, jawablah HANYA berdasarkan informasi atau langkah-langkah yang tertulis di KONTEKS. Jangan menambahkannya sendiri.
3. JANGAN BERHALUSINASI: Dilarang keras mengarang jawaban atau mengambil informasi dari internet (seperti harga, fitur yang tidak tertulis, dll).
4. KOMUNIKATIF SAAT KONTEKS TIDAK MENJAWAB: Jika pertanyaan masih berkaitan dengan Accurate Online namun informasi persisnya TIDAK ADA di dalam KONTEKS, JANGAN mengarang jawaban.
   Sebagai gantinya:
   - Sampaikan dengan sopan dan natural bahwa informasi yang dicari tidak ditemukan di modul pembelajaran.
   - Ajukan pertanyaan klarifikasi atau tawarkan bantuan terkait topik terdekat yang relevan untuk memastikan maksud pengguna.
5. KUTIPAN HALAMAN: Jika Anda memberikan jawaban berdasarkan konteks, Anda WAJIB mengutip referensi Halaman di akhir jawaban Anda (contoh: [Sumber: Halaman 2])."""
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    from langchain_core.prompts import PromptTemplate
    
    # KUNCI UTAMA PERBAIKAN: Format ulang dokumen agar LLM melihat nomor halamannya secara eksplisit!
    # Secara default, LangChain hanya mengirimkan 'page_content' saja tanpa metadata.
    document_prompt = PromptTemplate.from_template(
        "[Sumber Asli: Halaman {page}]\n{page_content}"
    )
    
    question_answer_chain = create_stuff_documents_chain(
        llm, 
        qa_prompt, 
        document_prompt=document_prompt
    )
    
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain

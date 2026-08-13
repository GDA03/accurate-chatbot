import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from rank_bm25 import BM25Okapi
import numpy as np

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
    def __init__(self, vectorstore, documents):
        self.vectorstore = vectorstore
        self.documents = documents
        
        # Inisialisasi BM25 (Sparse)
        tokenized_corpus = [doc.page_content.split(" ") for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
    def get_relevant_documents(self, query, top_k=5):
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
def get_llm():
    """Menggunakan Groq (Llama-3 70B) sebagai LLM utama karena lebih stabil dan cepat."""
    try:
        # Menggunakan Llama-3.3 70B via Groq untuk kualitas setara GPT-4
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2)
        return llm
    except Exception as e:
        print(f"Gagal memuat Groq: {e}")
        # Fallback ke Gemini Flash jika Groq bermasalah
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.2)
        return llm

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

def setup_rag_chain():
    # 1. Load Vector Store (Dense Search)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    # Ambil semua dokumen dari Chroma untuk BM25
    all_data = vectorstore.get()
    from langchain.schema import Document
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
        llm, ensemble_retriever, contextualize_q_prompt
    )
    
    # 3. RAG System Prompt (Kejujuran - W4 & W2)
    qa_system_prompt = """Anda adalah asisten AI untuk software Accurate Online.
Tugas Anda adalah menjawab pertanyaan user HANYA berdasarkan informasi dari KONTEKS di bawah ini.

KONTEKS:
{context}

ATURAN SANGAT KETAT:
1. Jawablah pertanyaan HANYA berdasarkan langkah-langkah atau informasi yang tertulis di KONTEKS. Jika konteks hanya menyebutkan 2 langkah, maka sebutkan 2 langkah itu saja. Jangan menambahkannya sendiri.
2. JANGAN PERNAH menambahkan informasi dari luar konteks, meskipun Anda tahu jawabannya (seperti tombol Sign Up, dll). Dilarang keras berhalusinasi.
3. Jika informasi untuk menjawab pertanyaan SAMA SEKALI TIDAK ADA di dalam KONTEKS, Anda WAJIB menjawab persis seperti ini:
"Maaf, informasi tersebut tidak tersedia di dalam Modul Pembelajaran."
4. Jika Anda menemukan jawabannya, Anda harus mengutip Halaman dari teks konteks di akhir jawaban Anda (contoh: [Sumber: Halaman 2])."""
    
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain

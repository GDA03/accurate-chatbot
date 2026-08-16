import os
from dotenv import load_dotenv
import pandas as pd
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import Dataset
from src.rag_pipeline import setup_rag_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from ragas.run_config import RunConfig

load_dotenv()

# ==========================================
# DATASET EVALUASI EMAS (Set A - Faktual)
# ==========================================
questions = [
    "Metode biaya persediaan apa saja yang tersedia di Accurate Online, dan apa perbedaannya?",
    "Ada berapa jenis barang di Accurate Online? Sebutkan beserta contohnya.",
    "Apakah Kategori Usaha yang saya pilih akan mempengaruhi laporan yang dihasilkan Accurate Online?",
    "Apa fungsi fitur Aset Tetap, dan apa yang harus saya buat lebih dulu sebelum bisa menginput data aset?",
    "Apa beda Penerimaan Barang dengan Faktur Pembelian?",
    "Saat membuat Faktur Pembelian, informasi apa yang sifatnya wajib diisi?",
    "Untuk apa data NPWP dan PTKP karyawan diisi di Accurate Online?"
]

# Jawaban Referensi (Berdasarkan Modul Pembelajaran)
# Idealnya disalin persis dari modul untuk pengujian yang presisi.
ground_truths = [
    "Terdapat dua metode biaya persediaan: FIFO (First In First Out) dan Average (Rata-rata). FIFO mengasumsikan barang yang pertama masuk adalah yang pertama keluar untuk dihitung biayanya. Average merata-ratakan biaya semua barang.",
    "Ada 3 jenis barang: Persediaan (contoh: stok barang dagangan), Non Persediaan (contoh: jasa, biaya kirim yang ditagihkan), dan Grup (paket barang seperti parsel).",
    "Ya. Kategori usaha yang dipilih pada saat Setup Awal akan menentukan jenis akun perkiraan bawaan (Chart of Accounts) yang secara otomatis dibuat oleh Accurate Online.",
    "Fitur Aset Tetap digunakan untuk mencatat harta perusahaan yang memiliki masa manfaat lebih dari setahun. Sebelum menginput aset tetap, pengguna harus membuat Kategori Aset terlebih dahulu.",
    "Penerimaan Barang adalah dokumen tanda terima barang secara fisik ke gudang. Sedangkan Faktur Pembelian adalah dokumen penagihan dari pemasok atas barang yang sudah dikirim.",
    "Informasi wajib yang harus diisi pada Faktur Pembelian adalah: Pemasok, Tanggal, Item Barang/Jasa, dan Harga.",
    "Data NPWP dan PTKP digunakan oleh sistem Accurate Online untuk menghitung pajak penghasilan (PPh 21) karyawan secara otomatis."
]

def generate_answers_and_contexts(rag_chain, qs):
    answers = []
    contexts = []
    
    print("Mulai menghasilkan jawaban untuk dataset evaluasi...")
    for q in qs:
        response = rag_chain.invoke({
            "input": q,
            "chat_history": []
        })
        answers.append(response["answer"])
        
        # Ekstrak konteks yang diambil oleh retriever
        retrieved_docs = response.get("context", [])
        page_contents = [doc.page_content for doc in retrieved_docs]
        contexts.append(page_contents)
        print(f"Selesai menjawab: '{q[:30]}...'")
        
    return answers, contexts

def main():
    rag_chain = setup_rag_chain()
    answers, contexts = generate_answers_and_contexts(rag_chain, questions)
    
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    
    dataset = Dataset.from_dict(data)
    
    print("\nMenyiapkan model Evaluator Ragas...")
    # Menggunakan ChatGroq (Llama-3.3 70B) yang sangat superior untuk Ragas
    eval_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, max_retries=20)
    # Embedding tetap menggunakan Gemini (limit embedding jauh lebih longgar)
    eval_embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    print("\nMenjalankan Evaluasi RAGAS (ini mungkin memakan waktu beberapa menit)...")
    
    # Menjalankan evaluasi menggunakan metrik Ragas standar dengan Gemini
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
        llm=eval_llm,
        embeddings=eval_embeddings,
        run_config=RunConfig(timeout=1200, max_workers=2, max_retries=20)
    )
    
    print("\n=== HASIL EVALUASI RAGAS ===")
    print(result)
    
    # Export ke Markdown untuk laporan yang lebih mudah dibaca
    df = result.to_pandas()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, "ragas_evaluation_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Laporan Evaluasi Ragas\n\n")
        f.write("Berikut adalah hasil pengujian akurasi Chatbot Accurate Online menggunakan **LLM-as-a-Judge (Gemini)**.\n\n")
        
        f.write("## 📈 Ringkasan Skor Metrik\n")
        for metric_name, score in result.items():
            f.write(f"- **{metric_name.replace('_', ' ').title()}**: {score:.4f}\n")
            
        f.write("\n---\n\n## 📝 Detail Pengujian per Pertanyaan\n\n")
        for index, row in df.iterrows():
            f.write(f"### Pertanyaan {index + 1}\n")
            f.write(f"**Q:** {row['question']}\n\n")
            f.write(f"**Kunci Jawaban (Ideal):**\n> {row['ground_truth']}\n\n")
            f.write(f"**Jawaban RAG Chatbot:**\n> {row['answer']}\n\n")
            
            f.write("**Skor Metrik Individual:**\n")
            if 'context_precision' in row and pd.notna(row['context_precision']):
                f.write(f"- Context Precision: {row['context_precision']:.4f}\n")
            if 'context_recall' in row and pd.notna(row['context_recall']):
                f.write(f"- Context Recall: {row['context_recall']:.4f}\n")
            if 'faithfulness' in row and pd.notna(row['faithfulness']):
                f.write(f"- Faithfulness: {row['faithfulness']:.4f}\n")
            if 'answer_relevancy' in row and pd.notna(row['answer_relevancy']):
                f.write(f"- Answer Relevancy: {row['answer_relevancy']:.4f}\n")
            f.write("\n---\n\n")
            
    print(f"\nLaporan Markdown yang rapi telah disimpan ke '{report_path}'")

if __name__ == "__main__":
    main()

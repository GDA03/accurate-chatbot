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
from datasets import Dataset
from rag_pipeline import setup_rag_chain

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
    
    print("\nMenjalankan Evaluasi RAGAS (ini mungkin memakan waktu)...")
    
    # Menjalankan evaluasi menggunakan metrik Ragas standar
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
    )
    
    print("\n=== HASIL EVALUASI RAGAS ===")
    print(result)
    
    # Export ke CSV untuk laporan
    df = result.to_pandas()
    df.to_csv("../ragas_evaluation_report.csv", index=False)
    print("\nLaporan detail telah disimpan ke 'ragas_evaluation_report.csv'")

if __name__ == "__main__":
    main()

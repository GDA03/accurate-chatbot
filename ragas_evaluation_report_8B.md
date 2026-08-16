# 📊 Laporan Evaluasi Ragas

Berikut adalah hasil pengujian akurasi Chatbot Accurate Online menggunakan **LLM-as-a-Judge (Gemini)**.

## 📈 Ringkasan Skor Metrik
- **Context Precision**: 0.9417
- **Context Recall**: 0.7381
- **Faithfulness**: 0.6857
- **Answer Relevancy**: 0.7736

---

## 📝 Detail Pengujian per Pertanyaan

### Pertanyaan 1
**Q:** Metode biaya persediaan apa saja yang tersedia di Accurate Online, dan apa perbedaannya?

**Kunci Jawaban (Ideal):**
> Terdapat dua metode biaya persediaan: FIFO (First In First Out) dan Average (Rata-rata). FIFO mengasumsikan barang yang pertama masuk adalah yang pertama keluar untuk dihitung biayanya. Average merata-ratakan biaya semua barang.

**Jawaban RAG Chatbot:**
> [Sumber: Halaman 5]

Metode biaya persediaan yang tersedia di Accurate Online adalah Rata-rata dan FIFO (First-In-First-Out). 

- **Rata-rata**: Metode ini menghitung total nilai persediaan dibagi dengan total kuantitas barang.
- **FIFO**: Metode ini dimana barang yang pertama masuk akan dikeluarkan dan digunakan terlebih dahulu.

**Skor Metrik Individual:**
- Context Precision: 0.8875
- Context Recall: 1.0000
- Faithfulness: 0.8000
- Answer Relevancy: 0.9666

---

### Pertanyaan 2
**Q:** Ada berapa jenis barang di Accurate Online? Sebutkan beserta contohnya.

**Kunci Jawaban (Ideal):**
> Ada 3 jenis barang: Persediaan (contoh: stok barang dagangan), Non Persediaan (contoh: jasa, biaya kirim yang ditagihkan), dan Grup (paket barang seperti parsel).

**Jawaban RAG Chatbot:**
> Maaf, saya tidak dapat menjawab pertanyaan tersebut karena informasi tentang jenis barang di Accurate Online tidak ada di dalam konteks yang diberikan.

**Skor Metrik Individual:**
- Context Precision: 1.0000
- Context Recall: 0.5000
- Faithfulness: 0.0000
- Answer Relevancy: 0.0000

---

### Pertanyaan 3
**Q:** Apakah Kategori Usaha yang saya pilih akan mempengaruhi laporan yang dihasilkan Accurate Online?

**Kunci Jawaban (Ideal):**
> Ya. Kategori usaha yang dipilih pada saat Setup Awal akan menentukan jenis akun perkiraan bawaan (Chart of Accounts) yang secara otomatis dibuat oleh Accurate Online.

**Jawaban RAG Chatbot:**
> [Sumber: Kategori Usaha, Informasi Informatif]

Kategori Usaha yang Anda pilih tidak akan mempengaruhi laporan yang dihasilkan Accurate Online. Informasi ini bersifat informatif dan tidak akan mempengaruhi laporan dan fitur di Accurate Online.

**Skor Metrik Individual:**
- Context Precision: 0.8875
- Context Recall: 0.5000
- Faithfulness: 1.0000
- Answer Relevancy: 0.8338

---

### Pertanyaan 4
**Q:** Apa fungsi fitur Aset Tetap, dan apa yang harus saya buat lebih dulu sebelum bisa menginput data aset?

**Kunci Jawaban (Ideal):**
> Fitur Aset Tetap digunakan untuk mencatat harta perusahaan yang memiliki masa manfaat lebih dari setahun. Sebelum menginput aset tetap, pengguna harus membuat Kategori Aset terlebih dahulu.

**Jawaban RAG Chatbot:**
> Fitur Aset Tetap di Accurate Online berfungsi untuk mencatat jumlah aset yang dimiliki oleh perusahaan, sekaligus memantau atas penyusutan aset dan nilai buku aset.

Sebelum bisa menginput data aset, Anda harus membuat Kategori Aset Tetap terlebih dahulu. Kategori Aset Tetap ini berfungsi untuk mengelompokkan aset berdasarkan karakteristik, kegunaan, dan perannya dalam kegiatan perusahaan, sehingga memudahkan dalam pencatatan, pengelolaan, dan pelaporan keuangan.

**Skor Metrik Individual:**
- Context Precision: 1.0000
- Context Recall: 0.5000
- Faithfulness: 1.0000
- Answer Relevancy: 0.7959

---

### Pertanyaan 5
**Q:** Apa beda Penerimaan Barang dengan Faktur Pembelian?

**Kunci Jawaban (Ideal):**
> Penerimaan Barang adalah dokumen tanda terima barang secara fisik ke gudang. Sedangkan Faktur Pembelian adalah dokumen penagihan dari pemasok atas barang yang sudah dikirim.

**Jawaban RAG Chatbot:**
> Menurut konteks yang disediakan, Penerimaan Barang dan Faktur Pembelian memiliki perbedaan sebagai berikut:

- Penerimaan Barang digunakan untuk mencatat nilai barang diterima saat terjadi transaksi penerimaan barang sebelum ditagih faktur pembelian barang terkait. [Sumber: Halaman 20]

- Faktur Pembelian digunakan untuk membuat tagihan atas transaksi pembelian yang sudah dilakukan. [Sumber: Halaman 60]

Dengan demikian, Penerimaan Barang adalah proses mencatat barang yang diterima, sedangkan Faktur Pembelian adalah proses membuat tagihan atas transaksi pembelian tersebut.

**Skor Metrik Individual:**
- Context Precision: 1.0000
- Context Recall: 1.0000
- Faithfulness: 1.0000
- Answer Relevancy: 0.9736

---

### Pertanyaan 6
**Q:** Saat membuat Faktur Pembelian, informasi apa yang sifatnya wajib diisi?

**Kunci Jawaban (Ideal):**
> Informasi wajib yang harus diisi pada Faktur Pembelian adalah: Pemasok, Tanggal, Item Barang/Jasa, dan Harga.

**Jawaban RAG Chatbot:**
> Informasi yang sifatnya wajib diisi saat membuat Faktur Pembelian adalah NPWP.

**Skor Metrik Individual:**
- Context Precision: 0.8167
- Context Recall: 0.6667
- Faithfulness: 0.0000
- Answer Relevancy: 0.8857

---

### Pertanyaan 7
**Q:** Untuk apa data NPWP dan PTKP karyawan diisi di Accurate Online?

**Kunci Jawaban (Ideal):**
> Data NPWP dan PTKP digunakan oleh sistem Accurate Online untuk menghitung pajak penghasilan (PPh 21) karyawan secara otomatis.

**Jawaban RAG Chatbot:**
> Data NPWP dan PTKP karyawan diisi di Accurate Online untuk perhitungan pajak otomatis.

**Skor Metrik Individual:**
- Context Precision: 1.0000
- Context Recall: 1.0000
- Faithfulness: 1.0000
- Answer Relevancy: 0.9600

---


# 📊 Laporan Evaluasi Ragas

Berikut adalah hasil pengujian akurasi Chatbot Accurate Online menggunakan **LLM-as-a-Judge (Gemini)**.

## 📈 Ringkasan Skor Metrik
- **Context Precision**: 0.8125
- **Context Recall**: 0.5625
- **Faithfulness**: 0.8472
- **Answer Relevancy**: 0.9101

---

## 📝 Detail Pengujian per Pertanyaan

### Pertanyaan 1
**Q:** Metode biaya persediaan apa saja yang tersedia di Accurate Online, dan apa perbedaannya?

**Kunci Jawaban (Ideal):**
> Terdapat dua metode biaya persediaan: FIFO (First In First Out) dan Average (Rata-rata). FIFO mengasumsikan barang yang pertama masuk adalah yang pertama keluar untuk dihitung biayanya. Average merata-ratakan biaya semua barang.

**Jawaban RAG Chatbot:**
> Di Accurate Online, terdapat dua metode biaya persediaan yang tersedia, yaitu:

1. **Rata-rata**: Metode ini menghitung total nilai persediaan dibagi dengan total kuantitas barang.
2. **FIFO (First-In-First-Out)**: Metode ini dimana barang yang pertama masuk akan dikeluarkan dan digunakan terlebih dahulu.

Perbedaan antara kedua metode ini terletak pada cara menghitung nilai persediaan dan urutan pengeluaran barang.

[Sumber: Halaman 5]

**Skor Metrik Individual:**
- Context Precision: 1.0000
- Context Recall: 1.0000
- Faithfulness: 0.5000
- Answer Relevancy: 0.9666

---

### Pertanyaan 2
**Q:** Ada berapa jenis barang di Accurate Online? Sebutkan beserta contohnya.

**Kunci Jawaban (Ideal):**
> Ada 3 jenis barang: Persediaan (contoh: stok barang dagangan), Non Persediaan (contoh: jasa, biaya kirim yang ditagihkan), dan Grup (paket barang seperti parsel).

**Jawaban RAG Chatbot:**
> Pada Accurate Online, terdapat beberapa jenis barang yang dapat dikelompokkan berdasarkan karakteristik atau jenis yang sama. Berikut adalah beberapa jenis barang beserta contohnya:

1. **Kategori Barang**: Pengelompokan item berdasarkan karakteristik atau jenis yang sama. Contoh: Kategori makanan, minuman, dsb.
2. **Merk Barang**: Pengelompokkan item berdasarkan merek yang sama. Contoh: Indodrink, dsb.
3. **Satuan Barang**: Satuan yang digunakan untuk menghitung/mencatat jumlah fisik/non fisik suatu item. Contoh: PCS, Lusin, Hari, dsb.

Namun, perlu diingat bahwa informasi tentang jenis barang secara spesifik tidak sepenuhnya dijelaskan di dalam konteks yang disediakan. [Sumber: Halaman 14]

**Skor Metrik Individual:**
- Context Precision: 0.5000
- Context Recall: 0.2500
- Faithfulness: 0.9167
- Answer Relevancy: 0.8788

---

### Pertanyaan 3
**Q:** Apakah Kategori Usaha yang saya pilih akan mempengaruhi laporan yang dihasilkan Accurate Online?

**Kunci Jawaban (Ideal):**
> Ya. Kategori usaha yang dipilih pada saat Setup Awal akan menentukan jenis akun perkiraan bawaan (Chart of Accounts) yang secara otomatis dibuat oleh Accurate Online.

**Jawaban RAG Chatbot:**
> Tidak, Kategori Usaha yang Anda pilih tidak akan mempengaruhi laporan yang dihasilkan Accurate Online. Informasi ini bersifat informatif saja. [Sumber: Halaman 5]

**Skor Metrik Individual:**
- Context Recall: 0.0000

---

### Pertanyaan 4
**Q:** Apa fungsi fitur Aset Tetap, dan apa yang harus saya buat lebih dulu sebelum bisa menginput data aset?

**Kunci Jawaban (Ideal):**
> Fitur Aset Tetap digunakan untuk mencatat harta perusahaan yang memiliki masa manfaat lebih dari setahun. Sebelum menginput aset tetap, pengguna harus membuat Kategori Aset terlebih dahulu.

**Jawaban RAG Chatbot:**
> Fitur Aset Tetap di Accurate Online berfungsi untuk mencatat jumlah aset yang dimiliki oleh perusahaan, sekaligus memantau atas penyusutan aset dan nilai buku aset. Sebelum bisa menginput data aset, Anda harus membuat Kategori Aset Tetap terlebih dahulu. Kategori aset tetap ini berfungsi untuk mengelompokkan aset berdasarkan karakteristik, kegunaan, dan perannya dalam kegiatan perusahaan, sehingga memudahkan dalam pencatatan, pengelolaan, dan pelaporan keuangan. [Sumber: Halaman 44]

**Skor Metrik Individual:**
- Context Precision: 0.7500
- Faithfulness: 1.0000

---

### Pertanyaan 5
**Q:** Apa beda Penerimaan Barang dengan Faktur Pembelian?

**Kunci Jawaban (Ideal):**
> Penerimaan Barang adalah dokumen tanda terima barang secara fisik ke gudang. Sedangkan Faktur Pembelian adalah dokumen penagihan dari pemasok atas barang yang sudah dikirim.

**Jawaban RAG Chatbot:**
> Penerimaan Barang dan Faktur Pembelian adalah dua proses yang berbeda dalam sistem Accurate Online.

Penerimaan Barang digunakan untuk mencatat barang yang diterima oleh perusahaan, tanpa harus ada pesanan pembelian sebelumnya. Proses ini melibatkan pengisian informasi seperti Terima Dari, Tanggal, Nomor Terima, dan detail barang yang diterima [Sumber: Halaman 58].

Faktur Pembelian, di sisi lain, digunakan untuk membuat tagihan atas transaksi pembelian yang sudah dilakukan. Proses ini melibatkan pengisian informasi seperti Pemasok, Tanggal, dan detail barang yang dibeli [Sumber: Halaman 60].

Jadi, Penerimaan Barang lebih fokus pada penerimaan fisik barang, sedangkan Faktur Pembelian lebih fokus pada pembuatan tagihan untuk transaksi pembelian. [Sumber: Halaman 58, Halaman 60]

**Skor Metrik Individual:**
- Faithfulness: 1.0000
- Answer Relevancy: 0.8989

---

### Pertanyaan 6
**Q:** Saat membuat Faktur Pembelian, informasi apa yang sifatnya wajib diisi?

**Kunci Jawaban (Ideal):**
> Informasi wajib yang harus diisi pada Faktur Pembelian adalah: Pemasok, Tanggal, Item Barang/Jasa, dan Harga.

**Jawaban RAG Chatbot:**
> Saat membuat Faktur Pembelian, informasi yang sifatnya wajib diisi adalah NPWP (Nomor Pokok Wajib Pajak) pada kolom perpajakan. Ini penting agar saat ada transaksi pembelian yang mengenakan pajak PPH 23, tidak dikenakan tarif pajak ganda. [Sumber: Halaman 38]

**Skor Metrik Individual:**
- Context Precision: 1.0000
- Context Recall: 1.0000
- Faithfulness: 0.6667
- Answer Relevancy: 0.9225

---

### Pertanyaan 7
**Q:** Untuk apa data NPWP dan PTKP karyawan diisi di Accurate Online?

**Kunci Jawaban (Ideal):**
> Data NPWP dan PTKP digunakan oleh sistem Accurate Online untuk menghitung pajak penghasilan (PPh 21) karyawan secara otomatis.

**Jawaban RAG Chatbot:**
> Data NPWP dan PTKP karyawan diisi di Accurate Online untuk keperluan perhitungan pajak otomatis, terutama untuk perhitungan PPh 21 karyawan. Informasi ini sangat penting karena akan berkaitan dengan perhitungan tarif PPh 21 karyawan. [Sumber: Halaman 51 dan Halaman 53]

**Skor Metrik Individual:**
- Faithfulness: 1.0000
- Answer Relevancy: 0.8838

---


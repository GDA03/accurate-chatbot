# Skenario Pengujian QA (Quality Assurance) RAG Chatbot

Dokumen ini berisi daftar pertanyaan terstruktur untuk melakukan demonstrasi dan pengujian kualitas (QA) terhadap sistem RAG Chatbot Accurate Online. Pertanyaan ini dirancang khusus untuk menguji tiga fitur utama (Nilai Tambah): Akurasi Konteks, Anti-Halusinasi, dan Memori Percakapan.

---

## 1. Pengujian Faktual & Akurasi Referensi (Context Retrieval)
*Tujuan: Membuktikan bahwa Chatbot mampu mencari informasi yang tepat di dalam PDF dan menyertakan referensi Halaman [Sumber: Halaman X] di akhir jawabannya.*

- **Pertanyaan 1:** "Bagaimana langkah-langkah membuat akun baru di Accurate Online?"
- **Pertanyaan 2:** "Apa saja data perusahaan yang perlu dilengkapi di halaman Persiapan Data Perusahaan?"
- **Pertanyaan 3:** "Sebutkan cara mengakses accurate.id melalui browser!"

**Ekspektasi Output:** Chatbot memberikan langkah-langkah yang akurat sesuai teks di Modul Pembelajaran, diakhiri dengan kutipan sumber yang tepat.

---

## 2. Pengujian Anti-Halusinasi (Guardrail Test)
*Tujuan: Membuktikan perlindungan sistem RAG dari halusinasi model LLM (Groq/Llama-3). Chatbot tidak boleh menjawab menggunakan pengetahuan umum internet jika informasinya tidak ada di modul.*

- **Pertanyaan 1:** "Berapa harga paket berlangganan bulanan Accurate Online?"
- **Pertanyaan 2:** "Siapa nama CEO atau pendiri dari PT Cipta Piranti Sejahtera?"
- **Pertanyaan 3:** "Apa perbedaan fitur antara Accurate Online dengan Accurate 5 Desktop?"
- **Pertanyaan 4:** "Apa aja produk mereka?"

**Ekspektasi Output:** Chatbot **wajib** merespons dengan: *"Maaf, informasi tersebut tidak tersedia di dalam Modul Pembelajaran."* (atau kalimat penolakan sejenis).

---

## 3. Pengujian Memori Konteks (Conversational Memory)
*Tujuan: Membuktikan bahwa modul `history_aware_retriever` bekerja dengan baik dan bot mampu mengingat konteks dari *chat* sebelumnya untuk menjawab pertanyaan lanjutan.*

- **Pertanyaan Utama:** "Bagaimana cara menginput Data Pelanggan baru?"
- *(Tunggu hingga chatbot memberikan jawaban)*
- **Pertanyaan Lanjutan 1:** "Lalu, bagaimana jika saya ingin mengedit data mereka yang sudah tersimpan sebelumnya?"
- **Pertanyaan Lanjutan 2:** "Apakah ada panduan lain terkait menu tersebut?"

**Ekspektasi Output:** Pada Pertanyaan Lanjutan 1, chatbot harus paham bahwa kata ganti "mereka" dan kata "data" merujuk secara spesifik pada "Data Pelanggan" yang dibahas sebelumnya, lalu mencarikan solusinya di PDF secara akurat.

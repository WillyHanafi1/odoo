# Buku Panduan Teknis n8n + Odoo 19 (Volume 3 & 4)

Dokumen ini berisi panduan teknis langkah demi langkah untuk mengeksekusi otomatisasi operasional dan kecerdasan buatan (AI).

---

## KATEGORI 3: Membunuh Kerjaan Manual (Ops/HR/Project)

## 15. Auto-Generate Project & 10 Task Checklist dari Won Deal
**Langkah n8n:**
1. **Node 1: Odoo / Webhook Trigger** -> Memicu saat `crm.lead` berubah ke tahap `Won`.
2. **Node 2: Odoo (Create Project)** 
   * **Model:** `project.project`. **Data:** `name` = "Project: " + `{{ $json.name }}`.
3. **Node 3: Set / Item Lists (Daftar Task)**
   * Buat Array statis berisi 10 nama tugas standar (Misal: "1. Kick-off Meeting", "2. Desain Logo", dst).
4. **Node 4: Odoo (Create Tasks - Loop)**
   * Node ini akan berjalan 10 kali secara berulang.
   * **Model:** `project.task`.
   * **Data:** `name` = `{{ $json.task_name }}`, `project_id` = `{{ $('Node 2').item.json.id }}`.

## 16. Onboarding Karyawan 1 Klik (Odoo -> Trello -> WA)
**Langkah n8n:**
1. **Node 1: Odoo Trigger** -> Saat `hr.employee` baru dibuat.
2. **Node 2: Trello** -> Operation: *Create Card/Board*. Undang `{{ $json.work_email }}`.
3. **Node 3: Gmail** -> Kirim HR Welcome Kit PDF.
4. **Node 4: WhatsApp** -> Pesan sapaan pribadi ke nomor HP karyawan baru.

## 17. Tombol Approve WA untuk PO/Cuti Odoo
**Langkah n8n:**
1. **Node 1: Odoo Trigger** -> Saat `purchase.order` diajukan untuk *Approval*.
2. **Node 2: WhatsApp / Telegram (Kirim Tombol/Interactive Message)**
   * Kirim pesan bot berisi detail harga.
   * Sisipkan Tombol (Interactive Button) "Approve" dan "Reject". Tiap tombol memuat URL Webhook unik dari n8n. Contoh `https://n8n-anda.com/webhook/approve?id={{ PO_ID }}`
3. **Pemisahan Workflow:** Buat *Workflow* baru berisi **Webhook Trigger** untuk mendengarkan klik bos.
4. **Node (Approve Odoo):** **Model:** `purchase.order`, **Operation:** `Execute Custom Method (action_button_confirm)`.

## 18. Bot Penagih Deadline Telegram H-2
**Langkah n8n:**
1. **Node 1: Schedule Trigger (Tiap Pagi)**
2. **Node 2: Odoo (Cari Task Hampir Telat)**
   * **Model:** `project.task`, **Filter:** `date_deadline` = lusa, `state` != `done`.
3. **Node 3: Telegram** -> Ping staf terkait.

## 19. Gudang Setor Foto Rak Mingguan
**Langkah n8n:**
1. **Node 1: Schedule Trigger (Jumat 4 Sore)**.
2. **Node 2: WhatsApp (Kirim Permintaan Foto ke Gudang)**.
3. **Workflow Terpisah (Terima Foto WA):** Webhook menangkap balasan gambar dari Kepala Gudang.
4. **Node Odoo (Upload Attachment):** Simpan foto tersebut ke dalam *record* Odoo `stock.picking` atau Odoo chatter sebagai bukti *Stock Opname*.

## 20. Auto-Log Timesheet WFH
**Langkah n8n:**
1. **Node 1: Clockify / Toggl Trigger** -> Saat timer dihentikan.
2. **Node 2: Code Node** -> Hitung jam (`end_time` - `start_time`).
3. **Node 3: Odoo (Create Timesheet)** -> **Model:** `account.analytic.line`, masukkan deskripsi dan durasi jam kerja karyawan tersebut ke proyek yang dituju.

## 21. n8n Duplicate Cleaner (Pembersih Database)
**Langkah n8n:**
1. **Node 1: Schedule Trigger (Minggu tengah malam)**.
2. **Node 2: Odoo (Cari Duplikat)** -> Cari `res.partner` dan temukan email yang jumlahnya > 1 pakai *Code Node*.
3. **Node 3: Odoo (Archive / Merge)** -> Gunakan API `action_archive` untuk mematikan secara halus (Soft Delete) salah satu kontak.

---

## KATEGORI 4: "THE PURE AI MAGIC" (WOW Factor Eksekutif)

## 22. AI Lead Validator (Klien Gembel vs Sultan)
**Langkah n8n:**
1. **Langkah:** Ekstrak chat awal klien dari WhatsApp/Email.
2. **Node ChatGPT (Prompt):** "Baca percakapan ini. Asumsikan apakah klien ini serius B2B (Minta SLA, tanya legalitas) atau cuma nanya-nanya harga iseng (B2C/perorangan). Beri skor 1-100 dan Tag 'VIP/Reguler'."
3. **Node Odoo (Update CRM):** Masukkan angka skor ke `probability` atau *priority stars*, ubah tag `VIP` atau `Reguler`.

## 23. AI Sentiment Analysis (Deteksi Orang Marah)
**Langkah n8n:**
1. **Node 1: Email / Helpdesk Trigger**.
2. **Node 2: ChatGPT (Prompt):** "Lakukan Sentiment Analysis pada keluhan ini. Keluarkan format JSON tunggal: { 'marah': true/false, 'rating': 1-100 }."
3. **Node 3: Odoo (Update Priority)** -> Jika *marah* = `true`, set bintang prioritas jadi 3 (Tertinggi) dan tugaskan ke Manager Support langsung.

## 24. AI Sales Development Rep (SDR - Bales Email Sendiri)
**Langkah n8n:**
1. **Langkah:** Saat email pertanyaan masuk di Inbox Odoo.
2. **Node ChatGPT:** Berikan instruksi dasar (*system prompt*): "Anda adalah Sales Representative bernama AI Seriaflow. Gaya bahasa Anda profesional, hangat, dan ramah. Ini katalog jasa kami [Teks Katalog]. Tolong buatkan *draft* balasan untuk email klien ini: {{ $json.body_email }}".
3. **Node Odoo (Create Message Draft):** Simpan balasan tersebut sebagai DRAFT di Odoo (*state* = draft), agar bisa direview manusia sebelum dikirim final.

## 25. Asisten AI Pribadi Direktur (Reporting Lisan/Chat via Telegram)
**Langkah n8n:**
1. **Node 1: Telegram Trigger** (Mendengar pesan obrolan bos).
2. **Node 2: AI Agent / Workflow AI n8n (Advanced)**
   * Berikan Bot akses "Tools" atau kueri n8n.
   * **Instruksi:** "Ubah pertanyaan alami bos ('omzet bulan ini berapa') menjadi parameter *Date Range* untuk Odoo".
3. **Node 3: Odoo (Ambil Data)** -> Tarik nilai total *Invoice* bulan ini.
4. **Node 4: Telegram (Balas)** -> Kirim balik nominal dengan format yang dirapikan.

## 26. Membuat Penawaran (Quotation) Pakai Pesan Suara WA
**Langkah n8n:**
1. **Node 1: WhatsApp Trigger (Tipe Suara/Audio)**.
2. **Node 2: Download Audio** -> Ubah format ke MP3/OGG.
3. **Node 3: OpenAI (Whisper - Speech to Text)** -> Transkripsikan file suara.
4. **Node 4: ChatGPT (Info Extraction)**
   * **Prompt:** "Ekstrak nama klien, jasa yang dipesan, dan total harga dari teks ini: 'Bikinin penawaran web 5 juta untuk PT ABC'."
5. **Node 5: Odoo (Create SO)** -> **Model:** `sale.order`.
6. **Node 6: Odoo (Create SO Line)** -> **Model:** `sale.order.line`.
7. **Node 7: Odoo (Print PDF & Kirim Balik)** -> Menghasilkan laporan dari Odoo jadi PDF, lalu dikirim balik lewat WA ke *sales* tersebut saat itu juga. Ajaib!

*(Batas panduan teknis Kategori 3 dan 4)*

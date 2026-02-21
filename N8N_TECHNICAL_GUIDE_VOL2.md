# Buku Panduan Teknis n8n + Odoo 19 (Volume 2)
**Kategori 2: Menutup Kebocoran Sales & Leads**

Dokumen ini berisi panduan teknis langkah demi langkah (kombinasi *node* n8n dan pengaturan Odoo) untuk mengeksekusi 7 ide otomatisasi Kategori 2.

---

## 8. Log Transaksi Transparan: "Sales Saya Bilang Udah di-Follow Up, Bohong Nggak Ya?"
**Konsep:** Menggunakan fitur BCC Odoo atau integrasi n8n untuk mencatat setiap email/WA yang dikirim sales langsung ke tab *Chatter* di Odoo CRM.

**Langkah-langkah n8n:**
1. **Node 1: Webhook (Menerima Notifikasi dari WA/Email API)**
   * Buat *Webhook* di n8n untuk menerima Payload dari penyedia WA/Email setiap kali ada pesan keluar dari handphone/inbox sales.
2. **Node 2: Odoo (Mencari Lead Klien)**
   * **Model Name:** `crm.lead`
   * **Operation:** Get Many
   * **Filter:** `phone` = `{{ $json.body.nomor_tujuan }}` atau `email_from` = `{{ $json.body.email_tujuan }}`. (Mencari apakah klien ini ada di database).
3. **Node 3: Odoo (Catat ke Chatter CRM)**
   * **Model Name:** `mail.message`
   * **Operation:** Create
   * **Data:**
     * `res_id`: ID Lead dari Node 2.
     * `model`: `crm.lead`
     * `body`: `Log Komunikasi: Sales mengirim WA berbunyi: "{{ $json.body.pesan }}"`
     * `message_type`: `comment`

---

## 9. Fast Response: Form Web -> Langsung Notif Telepon
**Konsep:** Saat pelanggan mengisi Contact Form di website (Odoo Web atau WordPress), detik itu juga n8n mengirim notifikasi ke handphone / Slack si bos.

**Langkah-langkah n8n:**
1. **Node 1: Webhook / Odoo Trigger**
   * Jika pakai Odoo Website: Gunakan node *Odoo Trigger* (harus install modul khusus n8n-Odoo webhook) atau setel Automated Actions di Odoo untuk menembak webhook n8n saat `crm.lead` baru terbuat.
   * Jika WP/External: Node *Webhook* menerima data nama, email, HP.
2. **Node 2: Odoo (Create CRM Lead)**
   * **Model Name:** `crm.lead`
   * **Operation:** Create
   * **Data:** Masukkan Name, Contact Name, Email, Phone.
3. **Node 3: HTTP Request / Telegram / Slack (Peringatan Urgent)**
   * Kirim pesan bot ke grup sales/handphone: "🚨 LEAD BARU MASUK SAAT INI! Nama: {{ $json.contact_name }}. Nomor: {{ $json.phone }}. Segera hubungi sekarang untuk memenangkan deal!"

---

## 10. Filter Sultan (Bypass Prospek Kecil)
**Konsep:** Saat lead masuk, n8n mengecek ukuran perusahaan via API Clearbit. Jika perusahaannya kecil, beri jawaban email template otomatis. Jika perusahaannya besar, lemparkan ke Manager.

**Langkah-langkah n8n:**
1. **Node 1: Menerima Lead Baru (Webhook)**
   * Membawa data email prospek, contoh `budi@telkom.co.id`.
2. **Node 2: Clearbit / Apollo API / HTTP Request**
   * Tembak API Clearbit: `https://person.clearbit.com/v2/combined/find?email={{ $json.email }}`
   * Node ini akan mengembalikan data detail perusahaan (contoh: *Jumlah karyawan*, *Omzet*, dll).
3. **Node 3: If / Switch Node (Cabang Keputusan)**
   * **Kondisi:** Jika `{{ $json.company.metrics.employees }}` > 500 orang (Atau omzet > $1M).
   * **Jalur TRUE (Sultan):**
     * Node Odoo (Create Lead): `crm.lead`, assign `user_id` ke Sang Direktur Sales. Beri Tag "VIP/SULTAN".
     * Node Slack: Ping si Direktur.
   * **Jalur FALSE (Standard):**
     * Node Odoo (Create Lead): Assign ke Sales Biasa.
     * Node Send Email: Kirim PDF Company Profile umum.

---

## 11. Sistem Pemerataan Leads (Round-Robin)
**Konsep:** Membagi Leads yang masuk dari pameran/iklan secara bergilir (Misal: Sales A -> B -> C -> kembali ke A).

**Langkah-langkah n8n:**
1. **Node 1: Trigger (Lead Baru Masuk)**
2. **Node 2: Redis / Read-Write Data (Tracker Giliran)**
   * Karena n8n adalah *stateless* (tidak ingat run sebelumnya), gunakan *node* eksternal (Database, Airtable, atau variabel memori) untuk menyimpan angka "Giliran Siapa Sekarang" (Misal: 1, 2, atau 3).
3. **Node 3: Switch Node**
   * Jika 1 -> Assign Odoo Lead ke User_ID Sales A. Simpan Giliran = 2.
   * Jika 2 -> Assign Odoo Lead ke User_ID Sales B. Simpan Giliran = 3.
   * Jika 3 -> Assign Odoo Lead ke User_ID Sales C. Simpan Giliran = 1.
4. **Node 4: Odoo (Update Lead)**
   * Update *record* `crm.lead` dengan `user_id` yang terpilih.

---

## 12. Jepret Kartu Nama -> Otomatis Masuk Odoo (AI OCR)
**Konsep:** Sales memfoto kartu nama pakai HP (Telegram/WhatsApp), dikirim ke bot. n8n melempar foto itu ke AI (OpenAI Vision), diekstrak jadi teks, lalu dimasukkan ke Odoo.

**Langkah-langkah n8n:**
1. **Node 1: Telegram Trigger**
   * Menangkap pesan masuk berupa Gambar (Photo).
   * Download lampiran gambar tersebut ke dalam n8n.
2. **Node 2: OpenAI (Vision)**
   * Menggunakan ChatGPT-4o (atau Vision model).
   * **Prompt:** "Berikut adalah foto kartu nama. Tolong ekstrak data berikut dalam format JSON murni tanpa markdown: nama, jabatan, perusahaan, email, nomor_telepon."
   * Masukkan gambar dari Node 1.
3. **Node 3: JSON Parse**
   * Mengambil *output* teks JSON dari OpenAI menjadi variabel aktual.
4. **Node 4: Odoo (Create Lead/Contact)**
   * **Model Name:** `crm.lead` (atau `res.partner`)
   * **Operation:** Create
   * **Mapping:** `contact_name` = nama, `email_from` = email, `phone` = nomor_telepon, `partner_name` = perusahaan.
5. **Node 5: Telegram (Balasan)**
   * Bot membalas ke HP Sales: "✅ Kartu nama Bapak {{ nama }} sukses tersimpan ke Odoo CRM."

---

## 13. Ghosting Re-engagement (Email "Teguran" Bos)
**Konsep:** Mencari Lead yang sepi interaksi selama 14 hari, lalu otomatis diledakkan email dengan nama/tandatangan CEO.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger (Tiap Minggu Sore)**
2. **Node 2: Odoo (Cari Dead Leads)**
   * **Model:** `crm.lead`
   * **Filter 1:** `state` / `stage_id` = Tahap "Proposition" atau "Negotiation" (Bukan Won/Lost).
   * **Filter 2:** `write_date` <= `{{ $today.minus(14, 'days') }}` (Sudah lewat 2 minggu).
3. **Node 3: Send Email / Gmail**
   * Hubungkan ke akun email Bos (misal CEO@perusahaan.com).
   * **To:** `{{ $json.email_from }}`
   * **Subject:** Pertanyaan terkait project kita
   * **Body:** "Halo Pak/Bu {{ $json.contact_name }}, Saya [Nama CEO], CEO PT Maju. Tim saya menginfokan ada penawaran yang menggantung. Apakah masih ada hal yang membuat ragu? Jangan ragu balas email saya langsung."

---

## 14. Klien VIP Komplain -> Sirine Handphone Bos
**Konsep:** Membedakan keluhan pelanggan elit vs gratisan. Kalau VIP yang ngeluh, prioritas 1.

**Langkah-langkah n8n:**
1. **Node 1: Odoo / Webhook / Email Trigger (Tiket Masuk)**
   * Mendeteksi ada Helpdesk Ticket atau Email Komplain baru masuk.
2. **Node 2: Odoo (Cek Status VIP)**
   * **Model:** `res.partner`
   * Berdasarkan email pengirim tiket, cek apakah `partner` tersebut memiliki `category_id` (Tags) yang bernama "VIP" atau "Tier 1".
3. **Node 3: If Node**
   * Jika Tag = VIP -> Lanjut ke Node 4. Jika bukan -> Selesai (Biar CS biasa yang balas besok).
4. **Node 4: Panggilan Darurat (Twilio Voice / Telegram Call)**
   * Gunakan API seperti Twilio Programmable Voice untuk langsung menelepon nomor HP Direktur dengan pesan suara robot: "Waspada Pak. Klien VIP PT Delta mengirim komplain kritis ke sistem. Mohon segera di-handle."
   * Atau *Ping* khusus mention di Slack/Telegram.
5. **Node 5: Odoo (Update Ticket Priority)**
   * Update tiket/Email tadi menjai *Priority: High* (Bintang 3).

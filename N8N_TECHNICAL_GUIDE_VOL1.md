# Buku Panduan Teknis n8n + Odoo 19 (Volume 1)
**Kategori 1: Menghentikan Uang yang Bocor (Invoicing & Cashflow)**

Dokumen ini berisi panduan teknis langkah demi langkah (kombinasi *node* n8n dan pengaturan Odoo) untuk mengeksekusi 7 ide otomatisasi Kategori 1.

---

### Persiapan Wajib (Prasyarat)
Sebelum memulai 7 ide di bawah, Anda wajib sudah menghubungkan Odoo ke n8n:
1. Di Odoo: Masuk modus pengembang (Developer Mode) > Settings > Users > Pilih User Anda > Account Security > **Generate New API Key**.
2. Di n8n: Ke menu Credentials > Add Credential > cari **Odoo API**.
3. Masukkan URL Odoo Anda (contoh: `http://ip-droplet:8069`), database, email user, dan *Paste* API Key tadi sebagai password.

---

## 1. Piutang Nyangkut? Sistem Peneror WhatsApp Otomatis H-1 dan H+3
**Konsep:** n8n mengecek Odoo setiap jam 8 pagi untuk mencari *Invoice* yang tanggal jatuh temponya besok (H-1) atau sudah lewat 3 hari (H+3), lalu menembak API WhatsApp untuk menagih.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger**
   * Aturan: Menjalankan *workflow* setiap hari (Days = 1) pada jam 08:00 AM.
2. **Node 2: Odoo (Cari Tagihan)**
   * **Resource:** Custom Model
   * **Model Name:** `account.move` (Tabel Invoice)
   * **Operation:** Get Many (Return All: True)
   * **Fields to Fetch:** `name, partner_id, amount_residual, invoice_date_due`
   * **Filter 1:** `state` = `posted` (Invoice resmi)
   * **Filter 2:** `payment_state` = `not_paid` (Belum lunas)
   * **Filter 3:** `move_type` = `out_invoice` (Tagihan Pelanggan)
   * **Filter 4 (Tanggal):** Di n8n, gunakan filter *Expression* untuk mendapatkan H-1 atau H+3. Gunakan rumus javascript n8n (`$today`).
3. **Node 3: Odoo (Cari Nomor HP Klien)**
   * **Resource:** Custom Model, **Model:** `res.partner`, **Operation:** Get
   * **Custom Model ID:** `={{ $json.partner_id[0] }}` (Menarik ID pelanggan dari node sebelumnya).
   * Node ini akan menghasilkan data `phone` atau `mobile`.
4. **Node 4: HTTP Request (Kirim WhatsApp)**
   * **Method:** POST
   * **URL:** Endpoint API vendor WhatsApp Anda (misal Fonnte/WATI).
   * **Body (JSON):** 
     ```json
     {
       "target": "{{ $json.mobile }}", 
       "message": "Halo, ini sistem otomatis. Tagihan nomor {{ $('Node 2').item.json.name }} senilai Rp {{ $('Node 2').item.json.amount_residual }} jatuh tempo pada {{ $('Node 2').item.json.invoice_date_due }}. Harap segera dibayar."
     }
     ```
5. **Node 5: Odoo (Log ke Chatter - Opsional tapi penting)**
   * **Model:** `mail.message`, **Operation:** Create
   * Tulis pesan log di `body` bot telah menagih hari ini, kaitkan (`res_id`) dengan ID Invoice.

---

## 2. Alarm Slack/WA Manajer Jika Quotation >50Jt Tidak Di-Follow Up
**Konsep:** Cari penawaran (Sales Order state = Draft/Sent) nilainya di atas Rp 50.000.000 yang sudah lebih dari 3 hari tidak berubah status, lalu lapor atasan.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger** (Misal dijalankan tiap jam 10 pagi).
2. **Node 2: Odoo (Cari Quotation Basi)**
   * **Model Name:** `sale.order`
   * **Operation:** Get Many
   * **Filter 1:** `state` = `draft` atau `sent`
   * **Filter 2:** `amount_total` >= `50000000`
   * **Filter 3 (Penting):** `write_date` <= `{{ $today.minus(3, 'days').toISO() }}` (Cari Quotation yang modifikasi terakhirnya lebih dari 3 hari lalu).
3. **Node 3: Odoo (Cari Nama Sales)**
   * **Model Name:** `res.users` > Tarik nama asli si pembuat quotation (`user_id`).
4. **Node 4: Slack / Telegram / HTTP Request (Kirim Notifikasi)**
   * Sambungkan ke node Slack atau Telegram Bot n8n.
   * **Pesan Text:** "🚨 URGENT: Quotation {{ $('Node 2').item.json.name }} senilai Rp {{ $('Node 2').item.json.amount_total }} ke pelanggan belum di-*follow up* oleh {{ $json.name }} selama lebih dari 3 hari! Segera tegur."

---

## 3. Auto-Draft Invoice Klien Retainer (+ Kirim Email)
**Konsep:** Meng- *generate* invoice otomatis setiap tanggal 1 dari daftar kontrak langganan. (Karena Odoo Community tidak punya modul *Subscriptions* penuh, kita akali via n8n).

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger** 
   * Aturan: Berjalan setiap **Cron** `0 8 1 * *` (Jam 8 pagi, setiap tanggal 1 setiap bulan).
2. **Node 2: Odoo (Cari Kontrak Aktif)**
   * Opsi A: Buat field *Checkbox* bantuan di tabel Klien (Partner) bernama `Is Retainer`, lalu cari data itu.
   * Opsi B: Cari berdasarkan Sales Order yang diberi Tag `Retainer`. **Model:** `sale.order`, **Filter:** `state` = `sale`, cari yang label customnya Retainer.
3. **Node 3: Odoo (Create Invoice Baru)**
   * **Model Name:** `account.move`
   * **Operation:** Create
   * **Data:** 
     * `move_type`: `out_invoice`
     * `partner_id`: `={{ $json.partner_id[0] }}`
     * `invoice_date`: `={{ $today.toISODate() }}`
4. **Node 4: Odoo (Tambahkan Baris Item - Line Invoice)**
   * **Model Name:** `account.move.line`
   * **Operation:** Create
   * **Data:**
     * `move_id`: ID dari Invoice yang baru terbuat di Node 3.
     * `name`: "Biaya Retainer Bulanan"
     * `quantity`: 1
     * `price_unit`: `={{ $json.amount_total }}` (Ambil dari harga kontrak dasar).
5. **Node 5: Gmail atau Send Email**
   * Kirim email ke alamat email klien. Beritahu invoice bulan ini sudah terbit (bisa sisipkan link ke portal Odoo jika diaktifkan).

---

## 4. n8n Membaca Mutasi Bank dari Email -> Lunasi Invoice Odoo
**Konsep:** n8n bertindak sebagai "Kasir". Ia membaca notif email dari BCA/Mandiri, mengekstrak nominal Rp, mencocokkan di Odoo, lalu menandai lunas. *Syarat: Pelanggan membayar dengan nominal unik (kode unik).*

**Langkah-langkah n8n:**
1. **Node 1: Email Read (IMAP) Trigger**
   * Konfigurasi IMAP ke email finance perusahaan Anda.
   * **Filter:** Hanya baca email dari `no-reply@klikbca.com` (atau bank terkait).
2. **Node 2: Item Lists (Text Extract / Regex)**
   * Gunakan Node *Code* (JavaScript) atau Regex untuk mengekstrak teks nominal uang dari body email.
   * Contoh JS: `let nominal = items[0].json.text.match(/Rp\s*([\d\.,]+)/)[1];` (Menghapus titik agar jadi angka murni).
3. **Node 3: Odoo (Cari Invoice Cocok)**
   * **Model Name:** `account.move`
   * **Operation:** Get Many
   * **Filter:** `amount_total` == Nominal unik dari email. `payment_state` = `not_paid`.
   * *Jika ketemu 1 data, lanjut ke Node 4.*
4. **Node 4: Odoo (Catat Pembayaran - Payment)**
   * **Model Name:** `account.payment`
   * **Operation:** Create
   * **Data:**
     * `partner_id`: (ID pelanggan dari hasil Node 3)
     * `amount`: (Nominal transfer)
     * `payment_type`: `inbound` (Uang masuk)
5. **Node 5: Odoo (Rekonsiliasi / Action Post)**
   * Agar Invoice Odoo berubah menjadi "Paid", *Payment* tersebut harus di-*post* dan divalidasi ke *Invoice*. Pada level lanjut, n8n menjalankan `action_post` JSON-RPC ke *Payment* tersebut.

---

## 5. Tagihan Vendor (PDF via Email) -> Auto Draft Vendor Bill
**Konsep:** Vendor disuruh email tagihan PDF ke `tagihan@PT-Kamu.com`. n8n menyedot lampiran (attachment) PDF tersebut dan membuat Draft Bill di Odoo.

**Langkah-langkah n8n:**
1. **Node 1: Email Read (IMAP) Trigger**
   * Download lampiran / *attachments* diaktifkan.
2. **Node 2: Odoo (Cari Vendor)**
   * **Model Name:** `res.partner`
   * Cari berdasarkan `email` = `{{ $json.from.address }}` (Mencari di database Odoo apakah email pengirim ini sudah terdaftar sebagai vendor). Ambil `id`-nya.
3. **Node 3: Odoo (Create Vendor Bill Draft)**
   * **Model Name:** `account.move`
   * **Operation:** Create
   * **Data:** 
     * `move_type`: `in_invoice` (Artinya ini adalah Tagihan Vendor/Hutang).
     * `partner_id`: (ID dari Node 2).
4. **Node 4: Odoo (Upload Attachment PDF)**
   * **Model Name:** `ir.attachment`
   * **Operation:** Create
   * Tautkan file PDF biner dari Node 1 ke ID *Vendor Bill* yang baru saja terbuat di Node 3.
   * *Hasil: Bagian finance membuka Vendor Bills Odoo, draf sudah ada dan PDF tagihan dari vendor sudah menempel di sebelah kanannya.*

---

## 6. Laporan Rekap Omzet Harian ke WhatsApp Bos
**Konsep:** N8n menjumlahkan semua *Invoice* yang di-*confirm* hari ini dan mengirim total Rupiahnya ke bos.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger**
   * Aturan: Setiap hari jam 17:00 (5 Sore).
2. **Node 2: Odoo (Cari Transaksi Hari ini)**
   * **Model Name:** `account.move`
   * **Operation:** Get Many
   * **Filter 1:** `state` = `posted`
   * **Filter 2:** `move_type` = `out_invoice`
   * **Filter 3:** `invoice_date` = `{{ $today.toISODate() }}`
3. **Node 3: Code Node (Sum / Penjumlahan JavaScript)**
   * Di n8n, node *Code* akan melooping hasil Node 2 dan menjumlahkan kolom `amount_total`.
   * ```javascript
     let total_omzet = 0;
     for (let item of $input.all()) {
       total_omzet += item.json.amount_total;
     }
     return [{json: { total: total_omzet, transaksi_count: $input.all().length }}];
     ```
4. **Node 4: HTTP Request (Kirim Notif)**
   * Kirim WA lewat API: "Lapor Pak Bos! Hari ini ada {{ $json.transaksi_count }} invoice terbit dengan total Omzet Rp {{ $json.total }}. Selamat libur!"

---

## 7. Alarm Kontrak Retainer Mau Habis
**Konsep:** Cari kontrak atau *Sales Order* yang periode selesainya 30 hari lagi, lalu beri peringatan.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger**
   * Jalan setiap hari jam 09:00 pagi.
2. **Node 2: Odoo (Cari Kontrak/Project Expiring)**
   * **Model Name:** `project.project` (Atau jika menyimpan *end_date* di `sale.order`).
   * **Operation:** Get Many
   * **Filter:** Tanggal berakhir (`date` atau field custom `end_date`) = `{{ $today.plus(30, 'days').toISODate() }}` (Persis 30 hari dari sekarang).
3. **Node 3: Odoo (Cari Account Manager)**
   * Cari *user_id* yang bertanggung jawab memegang klien/project tersebut.
4. **Node 4: Email / Slack / Telepon**
   * Kirim pesan ke *Account Manager*: "⚠️ Kontrak PT X akan habis dalam 30 hari. Hubungi kontak mereka sekarang untuk perpanjangan."

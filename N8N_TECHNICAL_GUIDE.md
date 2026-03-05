# Buku Panduan Teknis n8n + Odoo 19

Dokumen ini berisi panduan teknis langkah demi langkah untuk seluruh otomatisasi n8n + Odoo 19 Community, dibagi menjadi 4 kategori.

---

### Persiapan Wajib (Prasyarat)

Sebelum memulai, Anda wajib sudah menghubungkan Odoo ke n8n:
1. Di Odoo: Masuk modus pengembang (Developer Mode) > Settings > Users > Pilih User Anda > Account Security > **Generate New API Key**.
2. Di n8n: Ke menu Credentials > Add Credential > cari **Odoo API**.
3. Masukkan URL Odoo Anda (contoh: `http://ip-droplet:8069`), database, email user, dan *Paste* API Key tadi sebagai password.

---

# SECTION A: MENGHENTIKAN UANG YANG BOCOR (Invoicing & Cashflow)

Target: Owner, Finance Director. Fokus: Memastikan uang masuk tepat waktu.

---

## 1. Piutang Nyangkut? Sistem Peneror WhatsApp Otomatis H-1 dan H+3
> 🔴 **PRIORITAS TINGGI** | Kesulitan: ⭐6/10 | ROI: ⭐10/10

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
4. **Node 4: Code (Format Pesan + Rate Limit)**
   * Membatasi pengiriman agar tidak spam. Menyusun pesan yang sopan berdasarkan apakah ini H-1 (reminder) atau H+3 (tagihan).
5. **Node 5: HTTP Request (Kirim WhatsApp)**
   * **Method:** POST
   * **URL:** Endpoint API vendor WhatsApp Anda (misal Fonnte/WAHA).
   * **Body (JSON):**
     ```json
     {
       "target": "{{ $json.mobile }}",
       "message": "Halo, ini sistem otomatis. Tagihan nomor {{ $('Node 2').item.json.name }} senilai Rp {{ $('Node 2').item.json.amount_residual }} jatuh tempo pada {{ $('Node 2').item.json.invoice_date_due }}. Harap segera dibayar."
     }
     ```
6. **Node 6: Odoo (Log ke Chatter)**
   * **Model:** `mail.message`, **Operation:** Create
   * Tulis pesan log di `body` bot telah menagih hari ini, kaitkan (`res_id`) dengan ID Invoice.
7. **Node 7: Telegram (Notif Selesai ke Finance)**
   * Kirim notifikasi ke Finance Manager bahwa batch penagihan hari ini sudah dikirim.

---

## 2. Alarm Slack/WA Manajer Jika Quotation >50Jt Tidak Di-Follow Up
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐4/10 | ROI: ⭐7/10

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
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐6/10 | ROI: ⭐5/10

**Konsep:** Meng-*generate* invoice otomatis setiap tanggal 1 dari daftar kontrak langganan. Karena Odoo Community tidak punya modul *Subscriptions* penuh, pendekatan terbaik adalah **menduplikat Sales Order** yang sudah ada.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger**
   * Aturan: Berjalan setiap **Cron** `0 8 1 * *` (Jam 8 pagi, setiap tanggal 1 setiap bulan).
2. **Node 2: Odoo (Cari SO Retainer Aktif)**
   * **Model:** `sale.order`
   * **Filter:** `state` = `sale`, dan beri Tag atau field custom `is_retainer` = True.
3. **Node 3: Odoo (Copy / Duplicate SO)**
   * Gunakan method `copy` via JSON-RPC untuk menduplikat SO yang sudah ada. Odoo otomatis membuat SO baru lengkap dengan line items.
4. **Node 4: Odoo (Confirm SO Baru)**
   * Jalankan `action_confirm` pada SO baru sehingga statusnya menjadi `sale`.
5. **Node 5: Odoo (Create Invoice dari SO)**
   * Jalankan `_create_invoices` pada SO baru sehingga invoice draft tercipta otomatis dengan semua line, tax, dan perhitungan yang benar.
6. **Node 6: Gmail atau Send Email**
   * Kirim email ke alamat email klien. Beritahu invoice bulan ini sudah terbit (bisa sisipkan link ke portal Odoo jika diaktifkan).

---

## 4. ~~Baca Mutasi Bank~~ → Auto-Notif Konfirmasi Pembayaran ke Klien
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐3/10 | ROI: ⭐8/10

**Konsep (BARU):** Alih-alih berusaha membaca email bank yang format-nya fragile, pendekatan yang lebih aman: Saat Finance **manual mencatat payment** di Odoo, n8n otomatis mengirim konfirmasi WA ke pelanggan bahwa pembayaran sudah diterima, plus notif ke Bos.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: Parsing email bank (format berubah-ubah, regex fragile, risiko salah match tinggi)
- ✅ Baru: Data payment sudah pasti benar karena diinput manual Finance. Hanya perlu kirim notifikasi.

**Langkah-langkah n8n:**
1. **Node 1: Odoo Trigger / Schedule Trigger**
   * Opsi A: Gunakan Automated Action di Odoo `account.payment` saat `state` berubah ke `posted` → tembak webhook n8n.
   * Opsi B: Schedule setiap 30 menit, cek payment baru (`create_date` hari ini, `state` = `posted`).
2. **Node 2: Odoo (Ambil Detail Payment)**
   * **Model:** `account.payment`
   * Tarik `partner_id`, `amount`, `payment_date`, `ref`, `communication` (nomor invoice).
3. **Node 3: Odoo (Ambil Kontak Pelanggan)**
   * **Model:** `res.partner` → ambil `mobile`, `email`, `name`.
4. **Node 4: HTTP Request (Kirim WA Konfirmasi ke Pelanggan)**
   * Pesan: "✅ Terima kasih! Pembayaran Anda sebesar Rp {{ $json.amount }} untuk Invoice {{ $json.communication }} telah kami terima pada {{ $json.payment_date }}. Terima kasih atas kepercayaannya."
5. **Node 5: Telegram (Notif ke Bos)**
   * "💰 Payment diterima: Rp {{ $json.amount }} dari {{ $json.partner_name }}."

---

## 5. ~~Vendor PDF → Bill~~ → Auto-Reminder Vendor Bill Jatuh Tempo
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐3/10 | ROI: ⭐8/10

**Konsep (BARU):** Alih-alih mencoba OCR tagihan PDF vendor yang formatnya sangat bervariasi, pendekatan yang lebih praktis: n8n mengecek Vendor Bill di Odoo yang mendekati jatuh tempo dan mengirim reminder ke Finance Manager agar tidak ada denda keterlambatan.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: OCR PDF vendor (format beda-beda, AI error-prone, biaya Vision API mahal)
- ✅ Baru: Data sudah ada di Odoo, tinggal baca dan reminder. Zero error rate.

**Langkah-langkah n8n:**
1. **Node 1: Schedule Trigger**
   * Aturan: Setiap pagi jam 08:00.
2. **Node 2: Odoo (Cari Vendor Bill Hampir Jatuh Tempo)**
   * **Model Name:** `account.move`
   * **Operation:** Get Many
   * **Filter 1:** `move_type` = `in_invoice` (Vendor Bill)
   * **Filter 2:** `payment_state` = `not_paid`
   * **Filter 3:** `invoice_date_due` antara hari ini dan 3 hari ke depan.
3. **Node 3: Odoo (Ambil Nama Vendor)**
   * **Model:** `res.partner` → tarik nama vendor dari `partner_id`.
4. **Node 4: Telegram / WA (Kirim Reminder ke Finance Manager)**
   * Pesan: "⚠️ REMINDER: Tagihan vendor {{ $json.partner_name }} sebesar Rp {{ $json.amount_total }} (No: {{ $json.name }}) jatuh tempo {{ $json.invoice_date_due }}. Segera proses pembayaran untuk menghindari denda."

---

## 6. Laporan Rekap Omzet Harian ke WhatsApp Bos
> 🔴 **PRIORITAS TINGGI** | Kesulitan: ⭐3/10 | ROI: ⭐8/10

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
   * Kirim WA lewat API: "Lapor Pak Bos! Hari ini ada {{ $json.transaksi_count }} invoice terbit dengan total Omzet Rp {{ $json.total }}. Selamat istirahat!"

---

## 7. Alarm Kontrak Retainer Mau Habis
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐4/10 | ROI: ⭐7/10

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

---

# SECTION B: MENUTUP KEBOCORAN SALES & LEADS

Target: Sales Manager, CMO. Fokus: Konversi prospek menjadi uang.

---

## 8. Sinkronisasi Otomatis Facebook/TikTok Lead Ads ke Odoo CRM
> 🔴 **PRIORITAS TINGGI** | Kesulitan: ⭐5/10 | ROI: ⭐9/10

**Konsep:** Saat prospek mengisi *form* iklan di platform Meta atau TikTok, n8n seketika (*real-time*) menangkap data tersebut dan memasukkannya sebagai Lead baru di Odoo. Hal ini meniadakan kebiasaan mengunduh file CSV manual, sehingga *sales* dapat menghubungi prospek dalam hitungan detik.

**Langkah-langkah n8n:**
1. **Node 1: Meta/TikTok Lead Trigger**
   * Gunakan *webhook trigger* khusus n8n atau *node* integrasi resmi platform terkait (Facebook Lead Ads) saat ada *form* disubmit.
2. **Node 2: Data Cleansing (Code Node)**
   * Format nomor HP yang masuk agar sesuai standar (Contoh: Konversi awalan `08` atau `62` acak menjadi `+628`) menggunakan Regex di *node code*.
   * Validasi email bukan disposable/bouncing (gunakan regex sederhana).
3. **Node 3: Odoo (Create CRM Lead)**
   * **Model Name:** `crm.lead`
   * **Operation:** Create
   * **Data:** Masukkan nama prospek, nomor HP yang sudah dibersihkan, *email*, dan beri otomatis `tag_ids` sumber seperti "FB Ads" atau "TikTok Ads".

> **Catatan integrasi Data Cleansing:** Validasi HP dan email sudah *built-in* di Node 2 di atas, sehingga tidak perlu workflow data cleansing terpisah.

---

## 9. Fast Response: Form Web → Langsung Notif Telepon
> 🔴 **PRIORITAS TINGGI** | Kesulitan: ⭐3/10 | ROI: ⭐9/10

**Konsep:** Saat pelanggan mengisi Contact Form di website (Odoo Web atau WordPress), detik itu juga n8n mengirim notifikasi ke handphone / Slack si bos.

**Langkah-langkah n8n:**
1. **Node 1: Webhook / Odoo Trigger**
   * Jika pakai Odoo Website: Gunakan node *Odoo Trigger* atau setel Automated Actions di Odoo untuk menembak webhook n8n saat `crm.lead` baru terbuat.
   * Jika WP/External: Node *Webhook* menerima data nama, email, HP.
2. **Node 2: Data Cleansing (Code Node)**
   * Format HP ke standar `+62xx`. Validasi email basic.
3. **Node 3: Odoo (Create CRM Lead)**
   * **Model Name:** `crm.lead`
   * **Operation:** Create
   * **Data:** Masukkan Name, Contact Name, Email, Phone.
4. **Node 4: HTTP Request / Telegram / Slack (Peringatan Urgent)**
   * Kirim pesan bot ke grup sales/handphone: "🚨 LEAD BARU MASUK SAAT INI! Nama: {{ $json.contact_name }}. Nomor: {{ $json.phone }}. Segera hubungi sekarang untuk memenangkan deal!"

---

## 10. ~~Filter Sultan (Clearbit)~~ → AI Lead Scoring dari Percakapan
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐5/10 | ROI: ⭐8/10

**Konsep (BARU):** Alih-alih mengecek ukuran perusahaan via API Clearbit (mahal, data Indonesia sangat terbatas), gunakan AI untuk **membaca isi percakapan awal** lead dan menilai keseriusan dari bahasa yang digunakan.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: Clearbit API $99+/bulan, data Indonesia tidak ada, mayoritas pakai Gmail bukan domain perusahaan
- ✅ Baru: Gemini gratis tier sudah cukup, lebih akurat karena menilai dari *isi* bukan *metadata*

**Langkah-langkah n8n:**
1. **Node 1: Menerima Lead Baru (Webhook / Trigger dari workflow #8 atau #9)**
   * Membawa data pesan awal lead (form message, chat WhatsApp, atau email inquiry).
2. **Node 2: Gemini / ChatGPT (Scoring)**
   * **Prompt:** "Baca percakapan/pesan awal ini dari seorang prospek bisnis. Nilai keseriusan mereka dari 1-100. Tanda prospek serius: minta SLA/perjanjian, tanya legalitas, sebut budget spesifik, minta meeting. Tanda tidak serius: hanya tanya harga, pesan 1 baris, bahasa asal-asalan. Output JSON: { 'score': number, 'tag': 'VIP' | 'REGULER', 'reasoning': string }"
3. **Node 3: If / Switch Node (Cabang Keputusan)**
   * **Kondisi:** Jika `score` >= 70:
   * **Jalur VIP:** Assign `user_id` ke Sales Leader, set tag VIP, kirim Telegram ping ke manager.
   * **Jalur REGULER:** Assign ke Sales Biasa, kirim email company profile otomatis.
4. **Node 4: Odoo (Update CRM Lead)**
   * **Model:** `crm.lead`, **Operation:** Update
   * Set `priority` berdasarkan skor, tambah `tag_ids`, update `description` dengan reasoning AI.

---

## 11. Integrasi Pesanan E-Commerce / Marketplace ke Odoo
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐7/10 | ROI: ⭐5/10

**Konsep:** Saat pelanggan melakukan pembelian dari toko *online* atau marketplace, n8n secara otomatis mengimpor rincian pesanan dan menyulapnya menjadi draf *Sales Order* dan *Invoice* di Odoo.

> **Catatan:** Untuk pasar Indonesia, marketplace lokal (Tokopedia/Shopee) memiliki API yang sangat terbatas. Pertimbangkan fokus ke WooCommerce/Shopify jika target market internasional, atau WhatsApp Commerce untuk UMKM lokal.

**Langkah-langkah n8n:**
1. **Node 1: WooCommerce/Shopify Trigger**
   * Menangkap saat ada `Order Created` atau `Order Paid` dari platform *e-commerce*.
2. **Node 2: Odoo (Cari/Buat Kontak Partner)**
   * Cari via *email* (*Model:* `res.partner`). Apabila belum terdaftar, buat profil *customer* baru.
3. **Node 3: Odoo (Create Sales Order)**
   * **Model Name:** `sale.order`
   * **Operation:** Create
   * Tautkan ID kontak dari *node* sebelumnya.
4. **Node 4: Odoo (Loop Order Lines)**
   * Lakukan iterasi (*looping*) seluruh kerangka produk yang masuk di keranjang pesanan.
   * Tembakkan setiap data ke tabel Odoo `sale.order.line` sehingga rincian jumlah (*Quantity*) dan nominal (Harga) cocok seperti di *website*.

---

## 12. ~~OCR Kartu Nama~~ → Auto WhatsApp Follow-Up Sequence (Day 1/3/7)
> 🔴 **PRIORITAS TINGGI** | Kesulitan: ⭐5/10 | ROI: ⭐9/10

**Konsep (BARU):** Alih-alih memfoto kartu nama (niche, jarang dipakai, sudah ada app gratisan yang lebih baik), buat **drip campaign WA otomatis** yang benar-benar menghasilkan closing.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: OCR kartu nama (berapa kali sebulan dapat kartu nama? Ada CamCard/Google Lens gratis)
- ✅ Baru: Auto follow-up **setiap lead baru** = meningkatkan conversion rate 30-50%

**Langkah-langkah n8n:**
1. **Node 1: Webhook / Trigger (Lead Baru Masuk)**
   * Terpicu dari workflow #8 atau #9 saat lead baru tercatat di Odoo CRM.
2. **Node 2: HTTP Request (WA Hari 1 - Salam + Company Profile)**
   * Kirim pesan: "Halo {{ $json.contact_name }}, terima kasih sudah menghubungi kami! Ini profil singkat layanan kami: [link]. Ada yang bisa kami bantu?"
3. **Node 3: Wait Node (3 Hari)**
   * Diam selama 3 hari menunggu respons.
4. **Node 4: Odoo (Cek Status Lead)**
   * Cek apakah lead sudah pindah stage (sudah direspon/di-follow up manual oleh sales). Jika sudah → stop. Jika belum → lanjut.
5. **Node 5: HTTP Request (WA Hari 3 - Cek Minat)**
   * Kirim pesan: "Halo {{ $json.contact_name }}, apakah ada hal yang ingin ditanyakan lebih lanjut? Kami siap bantu kapan saja."
6. **Node 6: Wait Node (4 Hari)**
   * Tunggu 4 hari lagi.
7. **Node 7: HTTP Request (WA Hari 7 - Last Call)**
   * Kirim pesan: "Halo {{ $json.contact_name }}, kami ingin memastikan Anda tidak melewatkan promo kami bulan ini. Jika tertarik, balas pesan ini dan tim kami akan segera menghubungi."
8. **Node 8: Odoo (Update Lead - Mark sebagai Follow-Up Selesai)**
   * Tambahkan note di chatter bahwa auto follow-up sequence sudah selesai.

---

## 13. ~~Data Cleansing Mandiri~~ → Telah Digabung ke #8 dan #9
> *Fitur ini tidak lagi berdiri sendiri. Logika cleansing HP dan validasi email sudah diintegrasikan sebagai Node 2 di workflow #8 (Sync Ads) dan #9 (Form Web).*

---

## 14. ~~Ekstraksi NPWP/NIB~~ → Auto-Generate NDA/Kontrak Draft dengan AI
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐5/10 | ROI: ⭐7/10

**Konsep (BARU):** Alih-alih mengekstrak dokumen NPWP (sangat niche, vendor onboarding jarang), buat otomatisasi yang benar-benar menghemat waktu: AI yang mendraft kontrak/NDA otomatis saat deal hampir closing.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: Ekstraksi NPWP (vendor onboarding mungkin 1-3x/bulan, bisa diketik manual)
- ✅ Baru: Draft kontrak dibutuhkan **setiap deal** — menghemat 2-3 jam kerja legal per deal

**Langkah-langkah n8n:**
1. **Node 1: Odoo Trigger / Webhook**
   * Terpicu saat Quotation/SO di-update ke stage tertentu (misal "Negotiation") atau dari tombol custom.
2. **Node 2: Odoo (Ambil Detail SO + Partner)**
   * **Model:** `sale.order` dan `res.partner`
   * Tarik: nama klien, alamat, nilai proyek, scope pekerjaan, durasi.
3. **Node 3: Gemini / ChatGPT (Draft Kontrak)**
   * **System Prompt:** "Anda adalah Legal Assistant. Buatlah draft Perjanjian Kerja Sama / NDA berdasarkan data berikut. Gunakan format hukum Indonesia yang standar. Sertakan pasal lingkup pekerjaan, nilai kontrak, jangka waktu, kewajiban para pihak, kerahasiaan, dan penyelesaian sengketa."
   * **Input:** Data dari Node 2.
4. **Node 4: Convert To PDF (Code / HTML-to-PDF)**
   * Format hasil AI menjadi PDF yang rapi (bisa pakai library puppeteer atau HTML template).
5. **Node 5: Odoo (Attach PDF ke SO)**
   * **Model:** `ir.attachment`
   * Upload PDF kontrak draft dan tautkan ke SO terkait. Finance/Legal tinggal review dan finalisasi.

---

# SECTION C: MEMBUNUH KERJAAN MANUAL (Ops/HR/Project)

Target: COO, HR Manager, Project Manager. Fokus: Efisiensi waktu staf.

---

## 15. Auto-Generate Project & 10 Task Checklist dari Won Deal
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐4/10 | ROI: ⭐8/10

**Konsep:** Saat deal di CRM dimenangkan, n8n otomatis membuat Project baru + 10 task standar.

**Langkah n8n:**
1. **Node 1: Odoo / Webhook Trigger** → Memicu saat `crm.lead` berubah ke tahap `Won`.
2. **Node 2: Odoo (Create Project)**
   * **Model:** `project.project`. **Data:** `name` = "Project: " + `{{ $json.name }}`.
3. **Node 3: Set / Item Lists (Daftar Task)**
   * Buat Array statis berisi 10 nama tugas standar (Misal: "1. Kick-off Meeting", "2. Desain Logo", dst).
4. **Node 4: Odoo (Create Tasks - Loop)**
   * Node ini akan berjalan 10 kali secara berulang.
   * **Model:** `project.task`.
   * **Data:** `name` = `{{ $json.task_name }}`, `project_id` = `{{ $('Node 2').item.json.id }}`.

---

## 16. ~~Onboarding Karyawan~~ → Auto-Assign Task Saat Pindah Project
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐4/10 | ROI: ⭐7/10

**Konsep (BARU):** Alih-alih automasi HR onboarding (sangat jarang terjadi, dependensi Trello tidak relevan), buat automasi yang terjadi **jauh lebih sering**: saat karyawan di-assign ke project baru.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: Onboarding karyawan baru (1-5x/tahun, pakai Trello??)
- ✅ Baru: Assign project baru (10-20x/bulan), langsung generate task SOP

**Langkah n8n:**
1. **Node 1: Odoo Trigger / Schedule**
   * Terpicu saat `project.task` baru dibuat dan di-assign ke user, atau schedule cek harian.
2. **Node 2: Odoo (Cari Template Task untuk Project Type)**
   * Ambil daftar SOP task standar berdasarkan tipe project (misal: "Web Dev", "Design", "Consultation").
3. **Node 3: Odoo (Create Onboarding Tasks)**
   * **Model:** `project.task`
   * Buat task-task SOP standar: "Baca Brief", "Setup Akses", "Pelajari SOP", "Daily Standup", dll.
4. **Node 4: WA / Telegram (Notif ke Karyawan)**
   * Kirim pesan: "Halo {{ $json.employee_name }}, kamu sudah di-assign ke project '{{ $json.project_name }}'. Cek Odoo untuk melihat daftar task awalmu. Selamat bekerja!"

---

## 17. Tombol Approve WA untuk PO/Cuti Odoo
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐6/10 | ROI: ⭐6/10

**Konsep:** Atasan bisa approve Purchase Order atau request cuti langsung dari WA tanpa harus buka laptop. **Pendekatan simpel:** Kirim link URL webhook (bukan interactive button yang butuh approval Meta).

**Langkah n8n:**
1. **Node 1: Odoo Trigger** → Saat `purchase.order` diajukan untuk *Approval*.
2. **Node 2: WhatsApp / Telegram (Kirim Detail + Link)**
   * Kirim pesan bot berisi detail harga PO.
   * Sisipkan **2 URL link** (bukan interactive button):
     * Link Approve: `https://n8n-anda.com/webhook/approve?id={{ PO_ID }}&action=approve`
     * Link Reject: `https://n8n-anda.com/webhook/approve?id={{ PO_ID }}&action=reject`
3. **Workflow Terpisah: Webhook Listener**
   * **Node 1: Webhook Trigger** — mendengarkan klik bos dari link di atas.
   * **Node 2: If Node** — cek parameter `action`.
   * **Node 3 (Approve): Odoo** — `purchase.order`, jalankan `button_confirm`.
   * **Node 3 (Reject): Odoo** — `purchase.order`, jalankan `button_cancel`.
   * **Node 4: WA** — Balas ke bos: "✅ PO sudah di-approve" atau "❌ PO sudah di-reject."

---

## 18. Bot Penagih Deadline Telegram H-2
> 🔴 **PRIORITAS TINGGI** | Kesulitan: ⭐3/10 | ROI: ⭐8/10

**Konsep:** Setiap pagi, cek task project yang deadline-nya lusa, lalu ping staf terkait via Telegram.

**Langkah n8n:**
1. **Node 1: Schedule Trigger (Tiap Pagi jam 09:00)**
2. **Node 2: Odoo (Cari Task Hampir Telat)**
   * **Model:** `project.task`, **Filter:** `date_deadline` = lusa, `stage_id` bukan `done`/`cancelled`.
3. **Node 3: Odoo (Ambil Info User)**
   * **Model:** `res.users` → ambil nama dan kontak dari `user_ids`.
4. **Node 4: Telegram** → Ping staf: "⏰ DEADLINE H-2! Task '{{ $json.name }}' di project '{{ $json.project_name }}' harus selesai lusa. Segera kerjakan!"

---

## 19. ~~Gudang Foto Rak~~ → Alert Stok Minimum (Reorder Point)
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐4/10 | ROI: ⭐8/10

**Konsep (BARU):** Alih-alih meminta kepala gudang mengirim foto rak (over-engineered, bisa pakai grup WA biasa), buat automasi yang **benar-benar mencegah kerugian**: alert saat stok produk sudah di bawah batas minimum.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: Foto rak gudang (kepala gudang tinggal kirim ke grup WA, tidak perlu n8n)
- ✅ Baru: Stockout = kehilangan penjualan. Alert otomatis mencegah ini.

**Langkah n8n:**
1. **Node 1: Schedule Trigger (Setiap Pagi jam 07:00)**
2. **Node 2: Odoo (Cari Produk Stok Kritis)**
   * **Model:** `product.product`
   * **Operation:** Get Many
   * Gunakan Code Node untuk membandingkan `qty_available` dengan `reorder_min_qty` (atau field custom `min_stock`).
   * Filter produk yang `qty_available` < batas minimum.
3. **Node 3: Code (Format Laporan)**
   * Susun daftar produk kritis dalam format tabel sederhana:
   ```javascript
   let report = "🚨 STOK KRITIS:\n\n";
   for (let item of $input.all()) {
     report += `• ${item.json.name}: ${item.json.qty_available} unit (min: ${item.json.min_stock})\n`;
   }
   return [{json: {report}}];
   ```
4. **Node 4: WA / Telegram (Kirim ke Purchasing Manager)**
   * Kirim daftar stok kritis agar segera dilakukan reorder.

---

## 20. ~~Auto Timesheet~~ → Daily Standup Bot WA
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐6/10 | ROI: ⭐6/10

**Konsep (DIREVISI):** Alih-alih integrasi Clockify/Toggl (yang kebanyakan tim UMKM tidak pakai), buat bot WA yang melakukan daily standup otomatis setiap pagi.

**Langkah n8n:**
1. **Node 1: Schedule Trigger (Setiap pagi jam 09:00)**
2. **Node 2: Odoo (Cari Daftar Karyawan Aktif)**
   * **Model:** `hr.employee` → ambil list karyawan yang punya project aktif.
3. **Node 3: Loop + WA (Kirim Pertanyaan Standup)**
   * Kirim WA ke setiap karyawan: "Selamat pagi {{ $json.name }}! 📋 Apa task yang kamu kerjakan hari ini? Balas pesan ini."
4. **Workflow Terpisah: Webhook Listener Balasan WA**
   * **Node 1: WA Trigger** — terima balasan teks dari karyawan.
   * **Node 2: Odoo (Create Log/Note)** — catat balasan sebagai note di task atau timesheet di `account.analytic.line`.
   * **Node 3: Odoo (Update Task Description)** — tambahkan log harian ke deskripsi task terkait.

---

## 21. n8n Duplicate Cleaner (Pembersih Database)
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐6/10 | ROI: ⭐5/10

**Konsep:** Membersihkan kontak duplikat di database Odoo secara berkala.

**Langkah n8n:**
1. **Node 1: Schedule Trigger (Minggu tengah malam)**.
2. **Node 2: Odoo (Ambil Semua Kontak)**
   * **Model:** `res.partner` → Ambil semua kontak dengan `email` dan `name`.
3. **Node 3: Code Node (Deteksi Duplikat)**
   * Cari email yang muncul lebih dari 1 kali. Tandai yang ID-nya lebih besar sebagai duplikat (keep yang lebih lama).
4. **Node 4: Odoo (Archive Duplikat)**
   * Gunakan API `action_archive` pada kontak duplikat. **Jangan hard delete** — selalu archive dulu untuk jaga-jaga.
5. **Node 5: Telegram (Laporan Pembersihan)**
   * Kirim notif: "🧹 Database Cleanup selesai. {{ $json.count }} kontak duplikat telah di-archive."

---

# SECTION D: THE PURE AI MAGIC (WOW Factor Eksekutif)

Target: Inovator, CEO. Fokus: Menunjukkan kapabilitas AI yang nyata.

---

## 22. AI Lead Validator (Klien Gembel vs Sultan — Skor 1-100)
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐5/10 | ROI: ⭐7/10

**Konsep:** AI membaca percakapan awal klien dan memberi skor keseriusan. Sales hanya fokus ke yang skornya tinggi.

> **Catatan:** Workflow ini bisa digabungkan langsung dengan #10 (AI Lead Scoring dari Percakapan) sebagai satu rangkaian. Lihat detail teknis di #10.

**Langkah n8n:**
1. Ekstrak chat awal klien dari WhatsApp/Email.
2. **Node Gemini/ChatGPT (Prompt):** "Baca percakapan ini. Asumsikan apakah klien ini serius B2B (minta SLA, tanya legalitas, sebut budget) atau cuma nanya harga iseng. Beri skor 1-100 dan Tag 'VIP/Reguler'."
3. **Node Odoo (Update CRM):** Masukkan angka skor ke `priority` atau custom field, ubah tag `VIP` atau `Reguler`.

---

## 23. AI Sentiment Analysis (Deteksi Orang Marah) — Embed di CS Workflow
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐5/10 | ROI: ⭐4/10

**Konsep (DIREVISI):** Jangan buat sebagai workflow mandiri. **Sisipkan sebagai 1 node tambahan** di dalam workflow Customer Service yang sudah ada (misal `Customer Service Klinik WAHA`).

**Cara embed:**
1. Di workflow CS existing, setelah menerima pesan klien, **tambahkan 1 node Gemini:**
   * **Prompt:** "Lakukan Sentiment Analysis pada pesan ini. Keluarkan JSON: { 'marah': true/false, 'rating': 1-100 }."
2. **If Node:** Jika `marah` = true dan `rating` > 80:
   * Set prioritas tiket jadi URGENT.
   * Kirim ping ke Manager Support langsung.
   * Langsung escalate tanpa antri.

---

## 24. AI Sales Development Rep (SDR — Bales Email Sendiri)
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐6/10 | ROI: ⭐6/10

**Konsep:** AI membaca email pertanyaan lalu mendraft balasan profesional. Hasilnya disimpan sebagai DRAFT (bukan auto-send) agar bisa direview manusia.

**Langkah n8n:**
1. **Node 1: Email IMAP Trigger** — Saat email pertanyaan masuk di inbox.
2. **Node 2: Gemini/ChatGPT (Draft Balasan)**
   * **System Prompt:** "Anda adalah Sales Representative bernama [Nama]. Gaya bahasa Anda profesional, hangat, dan ramah. Ini katalog jasa kami [Teks Katalog]. Tolong buatkan *draft* balasan untuk email klien ini."
   * **Input:** Body email yang masuk.
3. **Node 3: Odoo (Create Message Draft)**
   * Simpan balasan sebagai DRAFT di Odoo chatter (*state* = draft), agar bisa direview manusia sebelum dikirim final.
4. **Node 4: Telegram (Notif ke Sales)**
   * "📧 Draft balasan email dari {{ $json.sender_name }} sudah siap. Cek di Odoo untuk review dan kirim."

---

## 25. Asisten AI Direktur (Reporting via Telegram — Menu Tombol)
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐5/10 | ROI: ⭐6/10

**Konsep (DIREVISI):** Alih-alih natural language processing yang kompleks dan error-prone, gunakan **menu tombol/command** di Telegram yang lebih reliable.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: NLP "ubah pertanyaan alami bos menjadi query Odoo" — sangat berat, sering salah interpret
- ✅ Baru: Command sederhana `/omzet`, `/piutang`, `/stok` — 100% akurat, mudah di-maintain

**Langkah n8n:**
1. **Node 1: Telegram Trigger** (Mendengar pesan obrolan bos).
2. **Node 2: Switch Node (Route berdasarkan Command)**
   * `/omzet` → Workflow ambil total invoice bulan ini
   * `/piutang` → Workflow ambil unpaid invoices
   * `/stok` → Workflow ambil stok kritis
   * `/sales` → Workflow ambil pipeline CRM
3. **Node 3: Odoo (Ambil Data sesuai command)**
   * Jalankan query Odoo yang sudah predefined untuk setiap command.
4. **Node 4: Code (Format Laporan)**
   * Rapikan data menjadi format Markdown Telegram yang mudah dibaca.
5. **Node 5: Telegram (Balas)**
   * Kirim laporan yang sudah diformat.

**Daftar Command yang disarankan:**
| Command | Output |
|---------|--------|
| `/omzet` | Total invoice confirmed bulan ini |
| `/omzet_hari` | Total invoice hari ini |
| `/piutang` | Daftar invoice belum dibayar |
| `/stok` | Produk yang stoknya kritis |
| `/sales` | Pipeline CRM (jumlah lead per stage) |
| `/top_klien` | 5 klien dengan omzet terbesar bulan ini |

---

## 26. ~~Quote via Voice Note~~ → Quick Quote Form via WA Bot
> 🟡 **PRIORITAS SEDANG** | Kesulitan: ⭐5/10 | ROI: ⭐8/10

**Konsep (BARU):** Alih-alih transkripsi voice note (Whisper error-prone untuk bahasa Indonesia, salah angka bisa fatal), gunakan **form interaktif WA** yang simple dan 100% akurat.

**Mengapa lebih baik dari konsep lama:**
- ❌ Lama: Voice note → Whisper → ChatGPT extraction → Odoo (7 node, "lima juta" vs "lima puluh juta" bisa fatal)
- ✅ Baru: Form terstruktur → langsung ke Odoo (5 node, zero ambiguity)

**Langkah n8n:**
1. **Node 1: WA Trigger / Telegram Trigger**
   * Sales kirim command `/quote` ke bot.
2. **Node 2: WA / Telegram (Kirim Form Pertanyaan Berurut)**
   * Bot bertanya satu per satu:
     1. "Nama klien?" → Sales balas: "PT ABC"
     2. "Jasa/produk apa?" → Sales balas: "Website development"
     3. "Harga total (Rp)?" → Sales balas: "15000000"
3. **Node 3: Odoo (Create SO + SO Line)**
   * **Model:** `sale.order` → Buat SO baru.
   * **Model:** `sale.order.line` → Buat line dengan nama jasa dan harga.
4. **Node 4: Odoo (Generate PDF Report)**
   * Gunakan Odoo report engine untuk generate PDF quotation.
5. **Node 5: WA / Telegram (Kirim PDF Balik ke Sales)**
   * "✅ Quotation untuk PT ABC sudah jadi! Lihat PDF terlampir."

---

*Dokumen ini menggabungkan dan memperbarui seluruh Volume 1-4 Panduan Teknis n8n + Odoo 19. Fitur yang tidak relevan telah diganti dengan alternatif yang memiliki ROI lebih tinggi dan implementasi lebih praktis.*

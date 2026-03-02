# Buku Panduan Teknis n8n + Odoo 19 (Volume 2)
**Kategori 2: Menutup Kebocoran Sales & Leads**

Dokumen ini berisi panduan teknis langkah demi langkah (kombinasi *node* n8n dan pengaturan Odoo) untuk mengeksekusi otomatisasi Kategori 2.

---

## 8. Sinkronisasi Otomatis Facebook/TikTok Lead Ads ke Odoo CRM
**Konsep:** Saat prospek mengisi *form* iklan di platform Meta atau TikTok, n8n seketika (*real-time*) menangkap data tersebut dan memasukkannya sebagai Lead baru di Odoo. Hal ini meniadakan kebiasaan mengunduh file CSV manual, sehingga *sales* dapat menghubungi prospek dalam hitungan detik.

**Langkah-langkah n8n:**
1. **Node 1: Meta/TikTok Lead Trigger**
   * Gunakan *webhook trigger* khusus n8n atau *node* integrasi resmi platform terkait (Facebook Lead Ads) saat ada *form* disubmit.
2. **Node 2: Data Cleansing (Code Node)**
   * Format nomor HP yang masuk agar sesuai standar (Contoh: Konversi awalan `08` atau `62` acak menjadi `+628`) menggunakan Regex di *node code*.
3. **Node 3: Odoo (Create CRM Lead)**
   * **Model Name:** `crm.lead`
   * **Operation:** Create
   * **Data:** Masukkan nama prospek, nomor HP yang sudah dibersihkan, *email*, dan beri otomatis `tag_ids` sumber seperti "FB Ads" atau "TikTok Ads".

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

## 11. Integrasi Pesanan E-Commerce Eksternal (Shopify/WooCommerce)
**Konsep:** Saat pelanggan melakukan pembelian (*checkout*) dari toko *online* atau platform *e-commerce* eksternal, n8n secara otomatis mengimpor rincian pesanan dan menyulapnya menjadi draf *Sales Order* dan *Invoice* (Tagihan) di Odoo, guna menghindari input dobel admin.

**Langkah-langkah n8n:**
1. **Node 1: WooCommerce/Shopify Trigger**
   * Menangkap/merekam seketika saat ada perubahan *status* menjadi `Order Created` atau `Order Paid` dari platform *e-commerce*.
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

## 13. Auto-Cleansing & Formatting Data Kontak (Data Quality Control)
**Konsep:** Memanfaatkan alur logika n8n untuk membersihkan format penulisan nomor *handphone* yang berantakan, dan secara cerdas memvalidasi keaslian *email* penanya sebelum data difilter dan diizinkan masuk ke CRM Odoo.

**Langkah-langkah n8n:**
1. **Node 1: Webhook (Menerima Payload Lead Baru)**
   * Menyerap data *lead* dari *form* eksternal mana pun yang dikirim klien acak.
2. **Node 2: Abstract API / Clearbit**
   * Melakukan verifikasi untuk mengecek bahwa *email* bukan *disposable* (email sampah sementara), tidak memantul (*bouncing*), dan berpotensi valid aktif.
3. **Node 3: Code Node (Regex)**
   * Menganut aturan "Pembersihan Nomor HP". Menghilangkan strip, kurung, dan mengubah setiap variasi nomor bodoh (misal awalan "08") menjadi nomor standar internasional yang bersih berawal kode `+62xx`.
4. **Node 4: Odoo (Filter Check & Create Lead)**
   * Apabila seluruh validasi tersebut mulus dilalui oleh *If Node*, terbitkan Lead yang higienis ke `crm.lead` Odoo.

---

## 14. Ekstraksi Dokumen Legal (NPWP/NIB) menggunakan AI Vision
**Konsep:** Mempermudah alur *Vendor Onboarding*. Calon *supplier* atau kontraktor baru cukup menyetorkan lampiran foto dokumen SPPKP/NPWP mereka lewat aplikasi pesan (*WhatsApp*). N8n dibantu AI lalu akan mencegat dan mengekstrak rincian legal itu, menghasilkan profil perusahaan *vendor* matang di Odoo.

**Langkah-langkah n8n:**
1. **Node 1: WhatsApp Trigger (Tangkapan Dokumen Masuk)**
   * Menerima potret atau scan bukti berformat PDF/JPG dokumen (contoh: NPWP).
2. **Node 2: OpenAI (Vision)**
   * Memberikan instruksi (*prompt*): "Teks dalam potret ini adalah dokumen legal wajib pajak di Indonesia. Bacalah seksama dan tarik informasi krusial: 'Nomor NPWP/VAT', 'Nama Resmi Perusahaan', dan 'Alamat Jalan' dalam luaran JSON."
3. **Node 3: JSON Parse**
   * Mentransformasikan variabel hasil bacaan AI menjadi daftar informasi sistem n8n.
4. **Node 4: Odoo (Create Vendor Profile)**
   * **Model Name:** `res.partner`
   * **Operation:** Create
   * Menjejalkan Nama Perusahaan ke kolom perusahaannya, memasukkan 15 digit angka pajak ke atribut `vat`, dan memberikan stempel centang bahwa entitas baru ini adalah seorang `supplier/vendor`.

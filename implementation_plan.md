# Rencana Integrasi Odoo 19 Community + n8n (Revisi)

Dokumen ini berisi revisi 30 fitur integrasi Odoo 19 Community dengan n8n, **tanpa kategori Marketing dan POS**. Fokus dialihkan ke penguatan operasional inti: **Inventory, Manufacturing, Purchasing,** serta pendalaman fitur **Accounting & HR**.

## Fokus Area
- **Core Business:** Sales, CRM, Invoicing, Purchasing.
- **Operations:** Inventory (WMS), Manufacturing (MRP), Repair.
- **Human Resources:** Recruitment, Employees, Attendance.
- **Utilities:** System, Reporting.

---

## 30 Fitur Integrasi (Odoo 19 + n8n)

### 🔥 CRM & Sales (Lead to Deal)
1.  **Web Inquiry Sync (Website External -> CRM)**
    *   **Trigger:** Form submit di website perusahaan.
    *   **Action:** n8n cleaning data -> Create Lead di Odoo.
    *   **Benefit:** Sentralisasi database prospek.

2.  **Lead Enrichment (CRM -> External Data)**
    *   **Trigger:** Lead baru masuk dengan email korporat.
    *   **Action:** n8n cek LinkedIn/Company Profile -> Update field "Industry", "Employee Count" di Odoo.
    *   **Benefit:** Data prospek lebih lengkap untuk sales.

3.  **Salesperson Router (CRM)**
    *   **Trigger:** Lead baru masuk.
    *   **Action:** Cek kota/produk -> Assign ke Sales Team yang sesuai (misal: "Team Jakarta" atau "Team B2B").
    *   **Benefit:** Distribusi tugas otomatis.

4.  **Instant Quotation Generator (Sales)**
    *   **Trigger:** Request form "Minta Penawaran" dengan detail produk.
    *   **Action:** Create Quotation draft -> Generate PDF -> Email ke customer.
    *   **Benefit:** Respon instan ke pelanggan.

5.  **Deal Approval Notification (CRM -> Management)**
    *   **Trigger:** Diskon di Quotation > 20%.
    *   **Action:** Kirim notifikasi ke Manajer via WA/Telegram untuk approval.
    *   **Benefit:** Kontrol margin penjualan.

6.  **Contract Generator (Sales -> DocuSign)**
    *   **Trigger:** Sales Order Confirmed.
    *   **Action:** Generate kontrak PDF -> Kirim ke e-sign platform.
    *   **Benefit:** Mempercepat proses legal.

### 💰 Finance & Accounting (Invoicing)
7.  **Auto-Invoice from SO (Sales -> Invoicing)**
    *   **Trigger:** Layanan telah dikirim (Service Delivered).
    *   **Action:** Auto-create Invoice (Draft) dari Sales Order.
    *   **Benefit:** Mencegah lupa tagih (Revenue leakage).

8.  **Payment Receipt Notification (Invoicing -> WA)**
    *   **Trigger:** Payment registered (Lunas).
    *   **Action:** Kirim WA "Terima kasih, pembayaran Rp X telah diterima."
    *   **Benefit:** Profesionalitas & konfirmasi instan.

9.  **Vendor Bill OCR (Gmail -> Invoicing)**
    *   **Trigger:** Email masuk title "Invoice" + Attachment PDF.
    *   **Action:** OCR scan -> Create Vendor Bill Draft di Odoo.
    *   **Benefit:** Hemat waktu input tagihan supplier.

10. **Overdue Invoice Chaser (Invoicing -> Email Personal)**
    *   **Trigger:** Invoice H+3 jatuh tempo.
    *   **Action:** Kirim email personal (bukan mass mail) dari akun Salesperson: "Halo, reminder tagihan..."
    *   **Benefit:** Penagihan yang lebih humanis tapi otomatis.

11. **Bank Transaction Sync (BCA/Mandiri -> Odoo)**
    *   **Trigger:** Email notifikasi transaksi bank masuk.
    *   **Action:** Parse email body -> Create Payment entry di Odoo.
    *   **Benefit:** Rekonsiliasi semi-otomatis tanpa fitur Enterprise.

12. **Expense from Chat (Telegram -> Odoo Expense)**
    *   **Trigger:** Foto bon dikirim ke bot Telegram.
    *   **Action:** Create HR Expense record + attach foto.
    *   **Benefit:** Memudahkan klaim reimbursement karyawan lapangan.

### 📦 Inventory & Logistics
13. **Low Stock Alert (Stock -> Procurement Team)**
    *   **Trigger:** Stok produk < Minimum Quantity.
    *   **Action:** Kirim alert ke Slack/WA tim gudang/purchasing.
    *   **Benefit:** Mencegah stockout.

14. **Delivery Status Update (Stock -> Customer)**
    *   **Trigger:** Delivery Order status "Done" (Barang keluar).
    *   **Action:** Kirim email/WA ke customer: "Barang Anda sedang dikirim. Resi: X".
    *   **Benefit:** Mengurangi pertanyaan "Barang saya mana?".

15. **Auto-Replenishment Request (Stock -> Purchase)**
    *   **Trigger:** Stok habis total.
    *   **Action:** Create Request for Quotation (RFQ) draft ke Supplier default.
    *   **Benefit:** Mempercepat proses restock.

16. **Slow Moving Stock Report (Stock -> Management)**
    *   **Trigger:** Cron bulanan.
    *   **Action:** Cek barang yang tidak bergerak > 6 bulan -> Lapor ke manajemen.
    *   **Benefit:** Optimasi gudang.

17. **Return Order Notification (Stock -> Sales)**
    *   **Trigger:** Ada penerimaan barang retur (Return Receipt).
    *   **Action:** Notifikasi Salesperson untuk follow up customer.
    *   **Benefit:** Customer service proaktif.

### 🛒 Purchasing (Procurement)
18. **Vendor Price Comparison (Purchase)**
    *   **Trigger:** RFQ dibuat.
    *   **Action:** Kirim email ke 3 vendor sekaligus minta harga.
    *   **Benefit:** Mendapatkan harga modal terbaik.

19. **PO Approval Request (Purchase -> Manager)**
    *   **Trigger:** Purchase Order > Rp 10 Juta.
    *   **Action:** Hold PO -> Kirim notifikasi approval ke Direktur.
    *   **Benefit:** Kontrol pengeluaran perusahaan.

20. **Supplier Performance Rating (Purchase)**
    *   **Trigger:** Barang diterima (Receipt).
    *   **Action:** Hitung selisih waktu (Janji vs Realisasi) -> Update rating vendor di GSheets/Note.
    *   **Benefit:** Evaluasi vendor berbasis data.

### 🏗️ Manufacturing & Repair
21. **MO Ready Alert (Manufacturing -> Production Team)**
    *   **Trigger:** Semua komponen tersedia (Available).
    *   **Action:** Notifikasi kepala produksi "MO #123 siap dikerjakan".
    *   **Benefit:** Mengurangi idle time produksi.

22. **Productivity Report (Manufacturing)**
    *   **Trigger:** Work Order selesai.
    *   **Action:** Log durasi pengerjaan -> Bandingkan dengan standar -> Report anomali.
    *   **Benefit:** Analisa efisiensi pabrik.

23. **Repair Status Update (Repair -> Customer)**
    *   **Trigger:** Status perbaikan berubah (Diagnosed -> Repaired).
    *   **Action:** Info ke customer "Laptop Anda sudah selesai diperbaiki".
    *   **Benefit:** Transparansi layanan servis.

### 👥 Human Resources (HR)
24. **CV Parser (Email -> Recruitment)**
    *   **Trigger:** Email lamaran masuk ke `jobs@company.com`.
    *   **Action:** Parse PDF CV -> Create Applicant di Odoo -> Isi Nama, Email, No HP otomatis.
    *   **Benefit:** Database kandidat rapi tanpa input manual.

25. **Auto-Reject Pelamar (Recruitment)**
    *   **Trigger:** Stage applicant dipindah ke "Rejected".
    *   **Action:** Kirim email sopan: "Terima kasih sudah melamar, tapi..."
    *   **Benefit:** Menjaga employer branding.

26. **Attendance Lateness Alert (Attendance -> HR)**
    *   **Trigger:** Check-in > jam 9 pagi.
    *   **Action:** Log ke HR spreadsheet / Notifikasi personal.
    *   **Benefit:** Disiplin karyawan.

27. **Offboarding Task List (HR -> Operations)**
    *   **Trigger:** Employee Resign/Terminated.
    *   **Action:** Create Task: "Cabut akses email", "Ambil laptop", "Stop Payroll".
    *   **Benefit:** Keamanan aset perusahaan.

28. **Interview Scheduler (Recruitment -> Calendar)**
    *   **Trigger:** Meeting interview dibuat di Odoo.
    *   **Action:** Kirim Google Calendar Invite ke kandidat + Link Zoom/Meet.
    *   **Benefit:** Profesionalisme proses rekrutmen.

### 🔧 Utilities & Reporting
29. **Morning Briefing (All -> Management)**
    *   **Trigger:** Jam 07:00 Pagi.
    *   **Action:** Summary: Saldo Bank (est), Sales kemarin, Stok kritis, Absensi hari ini.
    *   **Benefit:** Snapshot bisnis harian.

30. **Database & File Backup (System -> Cloud)**
    *   **Trigger:** Tengah malam.
    *   **Action:** Trigger backup -> Upload ke Google Drive / S3.
    *   **Benefit:** Disaster recovery plan.

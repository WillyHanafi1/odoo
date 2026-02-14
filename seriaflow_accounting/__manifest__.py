{
    'name': 'Seriaflow Accounting Lite',
    'version': '19.0.1.0.0',
    'summary': 'Lightweight accounting for Odoo Community - Chart of Accounts, Journal Entries, Expenses & P&L Report',
    'description': """
        Seriaflow Accounting Lite
        =========================
        Modul accounting sederhana untuk Odoo 19 Community Edition.
        
        Fitur:
        - Chart of Accounts (Daftar Akun standar Indonesia)
        - Journal Entries (Jurnal Umum dengan debit/credit)
        - Expense Tracker (Pencatatan pengeluaran dengan approval)
        - Dashboard keuangan
        - Laporan Profit & Loss (Laba Rugi)
    """,
    'author': 'Seriaflow',
    'website': 'https://seriaflow.com',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/account_data.xml',
        'views/account_views.xml',
        'views/journal_views.xml',
        'views/expense_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        'wizard/pnl_wizard_views.xml',
        'reports/pnl_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

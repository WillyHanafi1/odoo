{
    'name': 'Seriaflow Hello',
    'version': '19.0.1.0.0',
    'summary': 'Simple test module - Hello page on website',
    'description': """
        Modul test sederhana dari Seriaflow.
        Menampilkan halaman /hello di website Odoo.
    """,
    'author': 'Seriaflow',
    'website': 'https://seriaflow.com',
    'category': 'Website',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'views/hello_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

{
    'name': 'Seriaflow Home Menu',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Custom Home Menu for Odoo 19 Community Edition',
    'description': """
        Replaces the default login redirection of Odoo Community (which jumps to the first app)
        with an Enterprise-like Home Menu grid displaying all installed apps.
    """,
    'author': 'Seriaflow',
    'depends': ['web', 'base'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'seriaflow_home_menu/static/src/home_menu/**/*',
            'seriaflow_home_menu/static/src/patch/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

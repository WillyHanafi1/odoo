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
            'seriaflow_home_menu/static/src/home_menu/home_menu.scss',
            'seriaflow_home_menu/static/src/home_menu/home_menu.xml',
            'seriaflow_home_menu/static/src/home_menu/home_menu.js',
            'seriaflow_home_menu/static/src/patch/webclient_patch.js',
            'seriaflow_home_menu/static/src/home_menu_systray/home_menu_systray.xml',
            'seriaflow_home_menu/static/src/home_menu_systray/home_menu_systray.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

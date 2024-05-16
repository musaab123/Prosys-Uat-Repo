{
    'name': "Account Reports Sales Team Filter",
    'summary': """Account Reports Sales Team Filter """,
    'description': """""",
    'author': "ProSys",
    'website': "https://www.prosys-sa.com/",
    'license': 'OPL-1',
    'category': 'Accounting/',
    'version': '16.0.1',
    'depends': ['account','account_accountant','account_reports'],
    'data': [
        'views/template_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'prosys_account_reports/static/src/js/custom_account_reports.js'
        ],
        
    },

    'installable': True,
    'auto_install': False,
}

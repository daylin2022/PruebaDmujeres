# -*- coding: utf-8 -*-
{
    'name': 'CUSTOM POS',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': 'Daylin Murga',
    'contributors': ['Daylin Murga'],
    'website': 'https://www.example.com',
    'category': 'Extra Tools',
    'depends': ['point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale.assets': [
            'custom_pos/static/src/js/models.js',
            'custom_pos/static/src/js/paquetesButtons.js',
            'custom_pos//static/src/xml/**/*',
        ]
    },
    'installable': True
}

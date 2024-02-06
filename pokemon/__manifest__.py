# -*- coding: utf-8 -*-
{
    'name': "pokemon",

    'summary': """
        Mantenedor de Pokemos¡nes""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base',],

    'data': [
        'security/ir.model.access.csv',
        'views/pokemones_view.xml',
        'data/cron_pokemon.xml',
    ],
}

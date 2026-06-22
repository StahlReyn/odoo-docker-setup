{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "John Estate",
    'category': 'Category',
    'description': """
    This is a Module for Real Estate.
    """,
    'license': "LGPL-3",
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_menus.xml',
    ],
} # pyright: ignore[reportUnusedExpression]
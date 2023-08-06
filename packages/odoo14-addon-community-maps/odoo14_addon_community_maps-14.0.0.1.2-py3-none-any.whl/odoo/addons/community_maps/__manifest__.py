# -*- coding: utf-8 -*-
{
    'name': "community_maps",

    'summary': """
    Module to create and manage your map visualizations into a  website""",

    'author': "Coopdevs Treball SCCL",
    'website': "https://gitlab.com/coopdevs/community-maps-builder-backend",

    'category': 'community-maps',
    'version': '14.0.0.1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_rest',
        'base_rest_base_structure',
        'sale',
        'crm',
        'metadata'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/cm_menu_root.xml',
        'views/cm_menu_root_config.xml',
        'views/cm_map.xml',
        'views/cm_filter_group.xml',
        'views/cm_map_colorschema.xml',
        'views/cm_place.xml',
        'views/cm_place_presenter_metadata.xml',
        'views/cm_place_category.xml',
        'views/cm_form_model.xml',
        'views/cm_form_submission.xml',
        'views/cm_presenter_model.xml'
    ]
}

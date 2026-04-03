{
    "name": "My Law Firm",
    "version": "1.0",
    "category": "Custom",
    "description": """
Law Firm modules for odoo.
===================================================
""",
    "depends": ["base", "account"],
    "data": [
        "views/client_views.xml",
        "views/case_views.xml",
        "views/hearing_views.xml",
        "views/document_views.xml",
        "views/mark_paid_wizard_views.xml",
        "views/billing_views.xml",
        "security/ir.model.access.csv",
        "views/my_law_firm_menu.xml",
    ],
    "sequence": 1,
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

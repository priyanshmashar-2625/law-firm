from odoo import fields, models

class LawClient(models.Model):
    _name = "law.client"
    _description = "Law Client"
    
    name = fields.Char(string="Client Name", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    address = fields.Text(string="Address")

    client_type = fields.Selection(
        [
            ("individual", "Individual"),
            ("company", "Company"),
        ],
        string="Client Type",
        default="individual",
    )

    notes = fields.Html(string="Notes")

    case_ids = fields.One2many(
        comodel_name="law.case",
        inverse_name="client_id",
        string="Cases",
    )

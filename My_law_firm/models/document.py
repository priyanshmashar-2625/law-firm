from odoo import models, fields

class LawDocument(models.Model):
    _name = "law.document"
    _description = "Case Document"

    name = fields.Char(string="Document Name", required=True)

    case_id = fields.Many2one(
        comodel_name="law.case",
        string="case",
    )

    client_id = fields.Many2one(
        comodel_name="law.client",
        string="Client",
    )

    document_type = fields.Selection(
        [
            ("evidence", "Evidence"),
            ("contract", "Contract"),
            ("petition", "Petition"),
        ],
        string="Document Type",
    )

    file = fields.Binary(string="File")
    filename = fields.Char(string="Filename")

    upload_date = fields.Date(string="Upload date")

    notes = fields.Html(string = "Notes")
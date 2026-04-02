from odoo import fields, models, api

class LawCase(models.Model):
    _name = "law.case"
    _description = "Law Case"

    name = fields.Char(string="Case Title", required=True)
    case_number = fields.Char(string="Case Number")

    client_id = fields.Many2one(
        comodel_name="law.client",
        string="Client",
        required=True,
    )

    opponent_name = fields.Char(string="Opponent Name")

    case_type = fields.Selection(
        [
            ("civil", "Civil"),
            ("criminal", "Criminal"),
            ("corporate", "Corporate"),
        ],
        string="Case Type",
    )

    court_name = fields.Char(string="Court Name")
    filing_date = fields.Date(string="Filing Date")
    next_hearing_date = fields.Date(string="Next Hearing Date")

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="draft",
    )

    description = fields.Html(string="Description")

    hearing_ids = fields.One2many(
        comodel_name="law.hearing",
        inverse_name="case_id",
        string="Hearings",
    )

    document_ids = fields.One2many(
        comodel_name="law.document",
        inverse_name="case_id",
        string="Documents",
    )

    billing_ids = fields.One2many(
        comodel_name="law.billing",
        inverse_name="case_id",
        string="Bills",
    )

    @api.model_create_multi
    # Auto set active when case is created.
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("status", "active")
        return super().create(vals_list)
    
    #update next hearing date automatically
    def update_next_hearing(self):
        for case in self:
            if case.hearing_ids:
                dates = case.hearing_ids.mapped("hearing_date")
                case.next_hearing_date = max(dates)

from odoo import models, fields, api

class LawBilling(models.Model):
    _name = "law.billing"
    _description = "Case Billing"

    name = fields.Char(string="Bill Reference", required=True)

    case_id = fields.Many2one(
        comodel_name="law.case",
        string="Case",
    )

    client_id = fields.Many2one(
        comodel_name="law.client",
        string="Client",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    amount = fields.Monetary(String="Amount", currency_field="currency_id")

    billing_type = fields.Selection(
        [
            ("fixed", "Fixed"),
            ("hourly", "Hourly"),
        ],
        string="Billing Type",
    )

    billing_date_and_time = fields.Datetime(String="Billing date and time")

    status= fields.Selection(
        [
            ("draft", "Draft"),
            ("paid", "Paid"),
        ],
        string="Status",
        default="draft",
    )

    notes = fields.Html(string="Notes")

    @api.onchange("case_id")
    # Auto fill client from case
    def _onchange_case(self):
        if self.case_id:
            self.client_id = self.case_id.client_id

    # Mark as Paid
    def action_mark_paid(self):
        self.status = "paid"
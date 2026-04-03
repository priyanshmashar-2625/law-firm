from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    amount = fields.Monetary(string="Amount", currency_field="currency_id")

    billing_type = fields.Selection(
        [
            ("fixed", "Fixed"),
            ("hourly", "Hourly"),
        ],
        string="Billing Type",
    )

    billing_date_and_time = fields.Datetime(string="Billing date and time")

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("paid", "Paid"),
        ],
        string="Status",
        default="draft",
    )

    notes = fields.Html(string="Notes")
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        readonly=True,
        copy=False,
    )
    report_attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        string="Report Attachment",
        readonly=True,
        copy=False,
    )

    @api.onchange("case_id")
    # Auto fill client from case
    def _onchange_case(self):
        if self.case_id:
            self.client_id = self.case_id.client_id

    # Open wizard to confirm marking paid
    def action_mark_paid(self):
        self.ensure_one()
        if self.status == "paid":
            raise ValidationError("This billing is already marked as paid.")

        return {
            "name": "Confirm Mark Paid",
            "type": "ir.actions.act_window",
            "res_model": "mark.paid.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("My_law_firm.view_form_mark_paid_wizard").id,
            "target": "new",
            "context": {
                "default_billing_id": self.id,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.status == "paid":
                rec._generate_invoice_and_report()
        return records

    def write(self, vals):
        previous_status = {rec.id: rec.status for rec in self}
        result = super().write(vals)
        for rec in self:
            if previous_status.get(rec.id) != "paid" and rec.status == "paid":
                rec._generate_invoice_and_report()
        return result

    def _generate_invoice_and_report(self):
        self.ensure_one()

        if self.invoice_id:
            return

        if not self.client_id:
            raise ValidationError("Client is required before marking bill as paid.")
        if not self.amount or self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

        if not self.invoice_id:
            income_account = self.env["account.account"].search(
                [
                    ("company_ids", "in", self.env.company.id),
                    ("active", "=", True),
                    ("account_type", "=", "income"),
                ],
                limit=1,
            )

            if not income_account:
                raise ValidationError(
                    "No active income account found. Configure an income account first."
                )

            invoice_vals = {
                "move_type": "out_invoice",
                "partner_id": self.client_id.id,
                "invoice_date": (
                    self.billing_date_and_time.date()
                    if self.billing_date_and_time
                    else fields.Date.today()
                ),
                "invoice_origin": self.name,
                "currency_id": self.currency_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.name or "Legal Billing",
                            "quantity": 1.0,
                            "price_unit": self.amount,
                            "account_id": income_account.id,
                        },
                    )
                ],
            }
            invoice = self.env["account.move"].create(invoice_vals)
            invoice.action_post()
            self.invoice_id = invoice.id

        self.report_attachment_id = False

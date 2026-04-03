from odoo import api, fields, models
from odoo.exceptions import ValidationError

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
    closure_invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Closure Invoice",
        readonly=True,
        copy=False,
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

    def action_start(self):
        for rec in self:
            rec.status = "active"

    def action_close(self):
        for rec in self:
            paid_bills = rec.billing_ids.filtered(lambda bill: bill.status == "paid")
            if not paid_bills:
                raise ValidationError(
                    "At least one paid billing is required before closing the case."
                )

            rec._generate_case_closure_invoice(paid_bills)
            rec.status = "closed"

        if len(self) == 1:
            report_action = self.env.ref(
                "My_law_firm.action_report_law_case_closure", raise_if_not_found=False
            )
            if report_action:
                return report_action.report_action(self)

        return True

    def _generate_case_closure_invoice(self, paid_bills):
        self.ensure_one()
        if self.closure_invoice_id:
            return self.closure_invoice_id

        currency_ids = paid_bills.mapped("currency_id").ids
        if len(set(currency_ids)) > 1:
            raise ValidationError(
                "All paid bills must have the same currency to create a closure invoice."
            )

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

        invoice_lines = []
        for bill in paid_bills:
            invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "name": bill.name or "Legal Billing",
                        "quantity": 1.0,
                        "price_unit": bill.amount,
                        "account_id": income_account.id,
                    },
                )
            )

        invoice_vals = {
            "move_type": "out_invoice",
            "partner_id": self.client_id.id,
            "invoice_date": fields.Date.today(),
            "invoice_origin": self.case_number or self.name,
            "currency_id": paid_bills[0].currency_id.id or self.env.company.currency_id.id,
            "invoice_line_ids": invoice_lines,
        }
        invoice = self.env["account.move"].create(invoice_vals)
        invoice.action_post()
        self.closure_invoice_id = invoice.id
        return invoice

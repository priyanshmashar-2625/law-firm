from odoo import fields, models
from odoo.exceptions import ValidationError


class MarkPaidWizard(models.TransientModel):
    _name = "mark.paid.wizard"
    _description = "Mark Billing as Paid"

    billing_id = fields.Many2one(
        comodel_name="law.billing",
        string="Billing",
        required=True,
        readonly=True,
    )

    def action_confirm_mark_paid(self):
        self.ensure_one()
        billing = self.billing_id

        if not billing:
            raise ValidationError("Billing record not found.")

        if billing.status != "paid":
            billing.write({"status": "paid"})

        if not billing.invoice_id:
            raise ValidationError("Invoice was not generated.")

        invoice_report = self.env.ref("account.account_invoices", raise_if_not_found=False)
        if invoice_report:
            return invoice_report.report_action(billing.invoice_id)

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": billing.invoice_id.id,
            "view_mode": "form",
            "target": "current",
        }

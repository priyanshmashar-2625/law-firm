from odoo import models, fields, api

class LawHearing(models.Model):
    _name = "law.hearing"
    _description = "Case Hearing"

    name = fields.Char(string="Hearing Reference")

    case_id = fields.Many2one(
        comodel_name="law.case",
        string="Case",
        required=True,
    )

    hearing_date = fields.Datetime(string="Hearing Date and Time")
    judge_name = fields.Char(string="Judge Name")
    court_room = fields.Char(string="Court Room")

    outcome = fields.Selection(
        [
            ("pending", "Pending"),
            ("adjourned", "Adjourned"),
            ("completed", "Completed"),
        ],
        string="Outcome",
        default="pending",
    )

    notes = fields.Html(string="Notes")

    @api.model
    # Update case after hearing created
    def create(self, vals):
        case = super().create(vals)
        if case.case_id:
            case.case_id.update_next_hearing()
        return case
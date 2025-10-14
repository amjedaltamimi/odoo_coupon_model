from odoo import fields, models, api
from datetime import date

from odoo.exceptions import ValidationError


class Coupon(models.Model):
    _name = 'coupon.coupon'
    _description = 'Discount Coupon'

    name = fields.Char(string='Coupon Code', required=True, copy=False)
    partner_id = fields.Many2many('res.partner', string='Friend or Family Member', required=True)
    value = fields.Float(string='Fixed Value', required=True)
    usage_limit = fields.Integer(string='Usage Limit', default=1, required=True)
    used_count = fields.Integer(string='Used Count', readonly=True, default=0)
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], string='Status', default='active', readonly=True)

    template_ids = fields.Many2many('quotation.template', string="Applicable Templates")

    _sql_constraints = [
        ('unique_code', 'unique(name)', 'Coupon code must be unique!')
    ]

    date_availability = fields.Date(string="End coupon")
    days_remaining = fields.Integer(string="Reminder days", compute="_compute_days_remaining", store=False)

    @api.depends('date_availability')
    def _compute_days_remaining(self):
        for rec in self:
            if rec.date_availability:
                rec.days_remaining = (rec.date_availability - date.today()).days
            else:
                rec.days_remaining = 0

    @api.constrains("date_availability")
    def check_coupon_date_entry(self):
        today = date.today()
        for rec in self:
            if rec.date_availability<today:
                raise ValidationError("you cant set availability in past")



from odoo import fields, models, api
from datetime import date

from odoo.exceptions import ValidationError


class Coupon(models.Model):
    _name = 'coupon'
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
    coupon_line_ids = fields.One2many('coupon.line', 'coupon_id', string="Assigned Coupons")
    # حقل مؤقت لاختيار الأشخاص قبل إنشاء coupon.line
    # حقل مؤقت لاختيار الأشخاص قبل إنشاء coupon.line
    partner_ids_temp = fields.Many2many(
        'res.partner',
        'coupon_partner_temp_rel',
        'coupon_id',
        'partner_id',
        string="Select Partners"
    )

    coupon_line_ids = fields.One2many('coupon.line', 'coupon_id', string="Assigned Coupons")

    def action_assign_coupon(self):
        for rec in self:
            current_users = len(rec.coupon_line_ids)
            allow_user_number = rec.usage_limit
            if current_users >= allow_user_number:
                raise ValidationError(
                    f"The coupon '{rec.name}' has already beem assigned to {current_users} "
                    f" Maximum allowed users :{allow_user_number} "
                )

            for partner in rec.partner_ids_temp:
                # إذا الشخص مش موجود مسبقًا في Assigned Partners
                existing_line = self.env['coupon.line'].search([
                    ('coupon_id', '=', rec.id),
                    ('partner_id', '=', partner.id)
                ], limit=1)
                if not existing_line:
                    self.env['coupon.line'].create({
                        'coupon_id': rec.id,
                        'partner_id': partner.id,
                        'remaining_value': rec.value,
                    })

        rec.partner_ids_temp = False
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

    @api.constrains("value")
    def _cjeck_coupon_value(self):
        for rec in self :
            if rec.value<0:
                raise ValidationError("value mustn't  be smaller than zero ")
class CouponLine (models.Model):
    _name = 'coupon.line'
    _description = 'Coupon for Partner'

    coupon_id = fields.Many2one('coupon', string="Coupon", required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Assigned To', required=True)
    remaining_value = fields.Float(
        string='Remaining Value',
        compute='_compute_remaining_value',
        store=True
    )
    used_count = fields.Integer(string='Used Count', default=0)

    @api.model
    def create_coupon_lines(self, coupon_id, partners):
        """Create coupon lines for multiple partners"""
        coupon = self.env['coupon'].browse(coupon_id)

        @api.depends('total_used', 'coupon_id.value')
        def _compute_remaining_value(self):
            for line in self:
                if line.coupon_id:
                    line.remaining_value = line.coupon_id.value - line.total_used
                else:
                    line.remaining_value = 0
        lines = []
        for partner in partners:
            lines.append(self.create({
                'coupon_id': coupon.id,
                'partner_id': partner.id,
                'remaining_value': CouponLine.remaining_value
            }))
        return lines

    def use_coupon(self, amount, partner=None):
        """Use a certain amount of coupon for a specific partner"""
        for line in self:
            # تحقق من صاحب الكوبون إذا تم تمريره
            if partner and line.partner_id.id != partner.id:
                raise ValidationError(f"You are not allowed to use this coupon. ({partner.name} is not assigned)")

            if line.remaining_value <= 0:
                raise ValidationError(f"{line.partner_id.name}'s coupon has no remaining balance.")

            if line.remaining_value < amount:
                raise ValidationError(f"{line.partner_id.name} does not have enough coupon balance.")

            line.remaining_value -= amount
            line.used_count += 1

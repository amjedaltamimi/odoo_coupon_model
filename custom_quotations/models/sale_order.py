from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    template_id = fields.Many2one('quotation.template', string='Created from Template', readonly=True)
    coupon_id = fields.Many2one('coupon', string='Coupon')
    state = fields.Selection(
        selection_add=[
            ('applied_coupon', 'Coupon Applied'),
        ],
        string='Status',
        readonly=True,
        copy=False,
        tracking=True
    )
    total_before_coupon = fields.Monetary(
        string="Total Before Coupon",
        compute="_compute_total_before_coupon",
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    @api.depends('amount_untaxed', 'order_line.discount')
    def _compute_total_before_coupon(self):
        for order in self:
            total = sum(
                line.price_unit * line.product_uom_qty
                for line in order.order_line if not line._is_delivery()
            )
            order.total_before_coupon = total

    def apply_coupon(self):
        for order in self:
            if not order.coupon_id:
                raise UserError("Please select a coupon first.")

            coupon = order.coupon_id

            coupon_line = self.env['coupon.line'].search([
                ('coupon_id', '=', coupon.id),
                ('partner_id', '=', order.partner_id.id)
            ], limit=1)

            if not coupon_line:
                raise ValidationError("You are not allowed to use this coupon.")

            if coupon.state == 'expired' or (coupon.date_availability and coupon.date_availability < fields.Date.today()):
                raise ValidationError(f"Sorry, coupon {coupon.name} is expired.")

            if coupon_line.remaining_value <= 0:
                raise ValidationError("Your coupon balance is 0, you can't use it anymore.")

            if order.template_id and coupon.template_ids and order.template_id not in coupon.template_ids:
                raise ValidationError("This coupon is not valid for the selected quotation template.")

            if order.amount_untaxed <= 0:
                raise ValidationError("Cannot apply coupon to an empty quotation.")
            if order.amount_untaxed < 500:
                raise ValidationError("Coupon cannot be applied: the order total must be at least 500.")

            discount_amount = min(coupon_line.remaining_value, order.amount_untaxed)
            discount_percentage = (discount_amount / order.amount_untaxed) * 100


            for line in order.order_line:
                if not line._is_delivery():
                    line.discount = discount_percentage

            coupon_line.use_coupon(amount=discount_amount, partner=order.partner_id)

            order.state = 'applied_coupon'

        return True

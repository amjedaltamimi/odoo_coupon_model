from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    template_id = fields.Many2one('quotation.template', string='Created from Template', readonly=True)
    coupon_id = fields.Many2one('coupon.coupon', string='Coupon')


    def apply_coupon(self):

        for order in self:



            if not order.coupon_id:
                raise UserError("Please select a coupon first.")

            coupon = order.coupon_id

            if coupon.state == 'expired':
                pass

            if coupon.used_count >= coupon.usage_limit:
                raise UserError("This coupon has reached its usage limit.")
            if coupon.days_remaining == 0:
                raise ValidationError("This coupon availability has ended!")

            if order.template_id and coupon.template_ids and order.template_id not in coupon.template_ids:
                raise UserError("This coupon is not valid for the selected quotation template.")

            if order.amount_untaxed <= 0:
                raise UserError("Cannot apply coupon to an empty or zero-value quotation.")

            if coupon.value >= order.amount_untaxed:
                order.message_post(body=f"Coupon {coupon.code} not applied because its value exceeds the quotation total.")
                continue


            discount_percentage = (coupon.value / order.amount_untaxed) * 100


            for line in order.order_line:
                if not line._is_delivery():
                    line.discount = discount_percentage


            coupon.used_count += 1
            if coupon.used_count >= coupon.usage_limit:
                coupon.state = 'expired'




        return True

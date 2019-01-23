# -*- coding: utf-8 -*-
import logging
import random
import uuid

from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import UserError
from odoo.osv import expression

logger = logging.getLogger(__name__)


class Partner(models.Model):
	_inherit = 'res.partner'

	city_id = fields.Many2one('res.country.city', string='City')
	district_id = fields.Many2one('res.country.district', string='District')
	uuid = fields.Char(string='UUID', default=lambda x: uuid.uuid1(uuid.getnode(), random.getrandbits(48) | 0x010000000000))
	customer_code = fields.Char(string=u'客户编码')
	supplier_code = fields.Char(string=u'供应商编码')

	@api.one
	@api.constrains('customer_code', 'supplier_code')
	def _constrains_code(self):
		result1 = self.search([('customer_code', '=', self.customer_code)])
		result2 = self.search([('supplier_code', '=', self.supplier_code)])
		if self.customer_code:
			if len(result1) > 1:
				raise UserError(u'客户编码已存在')
		if self.supplier_code:
			if len(result2) > 1:
				raise UserError(u'供应商编码已存在')

	@api.onchange('city_id')
	def _onchange_city_id(self):
		if self.city_id:
			return {'domain': {'district_id': [('city_id', '=', self.city_id.id)]}}
		else:
			return {'domain': {'district_id': []}}

	@api.onchange('state_id')
	def _onchange_state_id(self):
		self.city_id = None
		self.district_id = None
		if self.state_id:
			return {'domain': {'city_id': [('state_id', '=', self.state_id.id)]}}
		else:
			return {'domain': {'city_id': []}}

	@api.model
	def create(self, vals):
		"""客商编号规则-新建做检查"""
		if vals.get('state_id'):
			if vals.get('customer'):
				if not vals.get('customer_code'):
					logger.info(u"判断有没有客户编码")
					cus_partner_code = self.env['ir.sequence'].sudo().next_by_code('res.partner.customer.code')
					logger.info(cus_partner_code)
					code = '.'+self.env['res.country.state'].sudo().browse(vals.get('state_id')).code+'.'
					logger.info(code)
					vals['customer_code'] = cus_partner_code.replace('.', code)
					logger.info(vals['customer_code'])
			if vals.get('supplier'):
				if not vals.get('supplier_code'):
					sup_partner_code = self.env['ir.sequence'].sudo().next_by_code('res.partner.supplier.code')
					code = '.'+self.env['res.country.state'].sudo().browse(vals.get('state_id')).code+'.'
					vals['supplier_code'] = sup_partner_code.replace('.', code)
		return super(Partner, self).create(vals)

	@api.multi
	def write(self, vals):
		"""客商编号规则编辑状态下检查"""
		# if not self.state_id.code and not vals.get('state_id'):
		# 	raise UserError(u"请填写地址：所在省")
		if vals.get('customer') or vals.get('supplier'):
			if not self.customer_code and vals.get('customer'):
				state_code = self.env['res.country.state'].sudo().browse(vals.get('state_id'))
				if state_code:
					cus_partner_code = self.env['ir.sequence'].sudo().next_by_code('res.partner.customer.code')
					code = '.'+state_code.code+'.'
					vals['customer_code'] = cus_partner_code.replace('.', code)
				if self.state_id.code:
					cus_partner_code = self.env['ir.sequence'].sudo().next_by_code('res.partner.customer.code')
					code = '.'+self.state_id.code+'.'
					vals['customer_code'] = cus_partner_code.replace('.', code)
			if not self.supplier_code and vals.get('supplier'):
				state_code = self.env['res.country.state'].sudo().browse(vals.get('state_id'))
				if state_code:
					sup_partner_code = self.env['ir.sequence'].sudo().next_by_code('res.partner.supplier.code')
					code = '.'+state_code.code+'.'
					vals['supplier_code'] = sup_partner_code.replace('.', code)
				if self.state_id.code:
					sup_partner_code = self.env['ir.sequence'].sudo().next_by_code('res.partner.supplier.code')
					code = '.'+self.state_id.code+'.'
					vals['supplier_code'] = sup_partner_code.replace('.', code)
		return super(Partner, self).write(vals)

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			name = record.name
			if record.customer_code or record.supplier_code:
				placeholder = None
				if record.supplier_code and record.customer_code:
					placeholder = '/'
				name = '[%s%s%s] %s' % (record.customer_code, placeholder, record.supplier_code, name)
				if record.supplier_code or record.customer_code:
					name = name.replace('False', '')
					name = name.replace('None', '')
			result.append((record.id, name))
		return result

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			domain = ['|', '|', ('customer_code', 'like', name), ('supplier_code', 'like', name), ('display_name', operator, name)]
			if operator in expression.NEGATIVE_TERM_OPERATORS:
				domain = ['&', '!']+domain[1:]
		accounts = self.search(domain+args, limit=limit)
		return accounts.name_get()

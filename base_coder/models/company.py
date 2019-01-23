# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError


class Company(models.Model):
	_inherit = 'res.company'

	code = fields.Char(string=u'公司编码', required=True)

	@api.one
	@api.constrains('code')
	def _constrains_code(self):
		if self.code:
			result = self.search([('code', '=', self.code)])
			if len(result) > 1:
				raise UserError(u'公司编码已存在')

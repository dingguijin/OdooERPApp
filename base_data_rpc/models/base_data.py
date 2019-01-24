# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RPCBaseData(models.Model):
    _name = 'rpc.base.data'
    _rec_name = 'name'
    _description = u"同步数据表设置"

    name = fields.Char(string=u'名称', required=True)
    model_id = fields.Many2one(comodel_name='ir.model', string=u'模型', required=True)
    model_name = fields.Char(string=u'模型名称')
    local_table = fields.Selection(string=u'本地数据表',
                                   selection=[('00', u'模型一致'), ('01', u'分开存放'), ],
                                   default='00', required=True)
    local_table_name = fields.Char(string=u'存放模型名')
    connection_relation = fields.Boolean(string=u'解决关联关系', default=False, help=u"当字段中存在关联表单时，自动建立关系表")
    field_ids = fields.One2many(comodel_name='rpc.base.data.line', inverse_name='rpc_id', string=u'字段列表')
    domain_ids = fields.One2many(comodel_name='rpc.base.data.domain', inverse_name='rpc_id', string=u'过滤规则')

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.model_name = self.model_id.model

    @api.constrains('field_ids')
    def constrains_field_ids(self):
        """ 判断字段列表中主键是否只有一个 """
        for res in self:
            f_number = 0
            for field in res.field_ids:
                if field.ttype == 'many2one' or field.ttype == 'many2many' or field.ttype == 'one2many':
                    raise UserError(u"目前暂不支持类型为：many2one、many2many、one2many的字段同步")
                if field.primary_key:
                    f_number += 1
            if f_number != 1:
                raise UserError(u"请配置字段列表中的唯一主键，并且主键只能为1个！")


class RPCBaseDataLine(models.Model):
    _name = 'rpc.base.data.line'
    _rec_name = 'desc'
    _description = u"数据同步字段"

    fields_id = fields.Many2one(comodel_name='ir.model.fields', string=u'字段', required=True)
    name = fields.Char(string=u'字段名')
    desc = fields.Char(string=u'摘要')
    ttype = fields.Selection(selection='_get_field_types', string=u'字段类型', required=True)
    primary_key = fields.Boolean(string=u'唯一主键')
    rpc_id = fields.Many2one(comodel_name='rpc.base.data', string=u'同步数据表', ondelete='cascade')

    @api.onchange('fields_id', 'rpc_id')
    def onchange_fields_id(self):
        model_id = self._context.get('model_id')  # 获取上下文
        return {'domain': {'fields_id': [('model_id', '=', model_id)]}}

    @api.onchange('fields_id')
    def onchange_field(self):
        if self.fields_id:
            self.name = self.fields_id.name
            self.desc = self.fields_id.field_description
            self.ttype = self.fields_id.ttype

    @api.model
    def _get_field_types(self):
        return sorted((key, key) for key in fields.MetaField.by_type)


class RPCBaseDataDomain(models.Model):
    _name = 'rpc.base.data.domain'
    _description = u"数据同步过滤规则"

    name = fields.Char(string=u'表达式', required=True)
    rpc_id = fields.Many2one(comodel_name='rpc.base.data', string=u'同步数据表', ondelete='cascade')

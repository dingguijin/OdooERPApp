# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging
import rpc_functions as rpc
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DataUploading(models.TransientModel):
    _name = 'rpc.data.uploading'
    _description = u"数据上传-上传"

    REPEATTYPE = [
        ('00', u'忽略'),
        ('01', u'删除'),
        ('02', u'替换'),
    ]
    # repeat_type = fields.Selection(string=u'重复处理方式', selection=REPEATTYPE, default='02', required=True)
    rpc_data = fields.Many2one(comodel_name='rpc.base.data', string=u'上传数据表', required=True)

    @api.multi
    def start_uploading(self):
        """开始上传操作"""
        logging.info(u"开始上传操作")
        rpc_data = self.rpc_data
        # 上传配置项内容
        rpc_url, rpc_db, username, password = rpc.get_rpc_condif()
        logging.info(u"上传的参数为url:{},db:{},username:{},pwd:{}".format(rpc_url, rpc_db, username, password))
        # 开始连接rpc
        model, uid = rpc.connection_rpc(rpc_url, rpc_db, username, password)
        # 组装需要上传的字段和模型名
        model_name = rpc_data.model_id.model
        fields_dict = self.pack_model_field_to_array(rpc_data)
        logging.info(u"需要上传的模型：{}".format(fields_dict))
        domain = list()
        for d in rpc_data.domain_ids:
            domain.append(rpc.string_transfer_list(d.name))
        logging.info(u"数据表过滤表达式:{}".format(domain))
        rpc.search_create(model, rpc_db, uid, password, model_name, domain, fields_dict)
        logging.info(u"数据上传完成")


    @api.model
    def pack_model_field_to_array(self, model):
        """获取上传的字段"""
        field_arr = []
        for field in model.field_ids:
            field_arr.append(field.name)
        return field_arr



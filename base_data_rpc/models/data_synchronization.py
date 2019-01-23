# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging
import rpc_functions as rpc
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DataSynchronization(models.TransientModel):
    _name = 'rpc.data.synchronization'
    _description = u"数据同步-读取"

    REPEATTYPE = [
        ('00', u'忽略'),
        ('01', u'删除'),
        ('02', u'替换'),
    ]
    repeat_type = fields.Selection(string=u'重复处理方式', selection=REPEATTYPE, default='02', required=True)
    rpc_data = fields.Many2one(comodel_name='rpc.base.data', string=u'同步数据表', required=True)

    @api.multi
    def start_synchronization(self):
        """开始同步操作"""
        logging.info(u"开始同步操作")
        rpc_data = self.rpc_data
        # 获取配置项内容
        rpc_url, rpc_db, username, password = rpc.get_rpc_condif()
        logging.info(u"获取的参数为url:{},db:{},username:{},pwd:{}".format(rpc_url, rpc_db, username, password))
        # 开始连接rpc
        model, uid = rpc.connection_rpc(rpc_url, rpc_db, username, password)
        # 组装需要获取的字段和模型名
        model_name = rpc_data.model_id.model
        fields_dict = self.pack_model_field_to_array(rpc_data)
        logging.info(u"需要获取的字段：{}".format(fields_dict))
        domain = list()
        for d in rpc_data.domain_ids:
            domain.append(rpc.string_transfer_list(d.name))
        logging.info(u"数据表过滤表达式:{}".format(domain))
        result = rpc.search_read(model, rpc_db, uid, password, model_name, domain, fields_dict)
        # 检查数据存放方式（如果为分开存放，则检查分卡存放的模型和字段是否存在）
        if rpc_data.local_table == '01':
            self.checkout_local_model(rpc_data.local_table_name, rpc_data)
            model_name = rpc_data.local_table_name
        # 将结果写入到本地数据库
        self.processing_results(model_name, result)

    @api.model
    def pack_model_field_to_array(self, model):
        """组装需要获取的字段和模型名"""
        field_arr = list()
        for field in model.field_ids:
            field_arr.append(field.name)
        return {'fields': field_arr}

    @api.multi
    def processing_results(self, model_name, result):
        """根据返回的结果写入本地数据库
        :param model_name: 数据表模型名
        :param result: 返回结果list
        """
        logging.info(u"本次共返回{}条返回的数据！".format(len(result)))
        # 获取主键字段
        data_line = self.env['rpc.base.data.line'].search(
            [('rpc_id', '=', self.rpc_data.id), ('primary_key', '=', True)])
        if not data_line:
            raise UserError(u"未配置字段主键！请维护")
        primary_key = data_line.name
        for res in result:
            # 判断该条数据是否存在
            s_res = self.env[model_name].sudo().search([(primary_key, '=', res.get(primary_key))])
            if s_res:
                if self.repeat_type == '00':
                    logging.info(u"数据>>:{}已存在，系统将忽略此条数据！".format(res.get(primary_key)))
                elif self.sudo().repeat_type == '01':
                    logging.info(u"数据>>:{}已存在，系统将删除此条数据！".format(res.get(primary_key)))
                    s_res.sudo().unlink()
                elif self.repeat_type == '02':
                    logging.info(u"数据>>:{}已存在，系统将替换此条数据！".format(res.get(primary_key)))
                    s_res.sudo().write(res)
            else:
                logging.info(u"数据>>:{}不存在，系统将主动创建！".format(res.get(primary_key)))
                self.env[model_name].sudo().create(res)
        return True

    @api.model
    def checkout_local_model(self, model_name, rpc_data):
        """检查本地模型
        :param model_name: 本地模型名称
        :param rpc_data: 选择的数据表
        :return boolean: 返回true or false
        """
        model = self.env['ir.model'].sudo().search([('model', '=', model_name)])
        if not model:
            msg = u"本地模型:'{}'不存在,请检查！".format(model_name)
            logging.info(msg)
            raise UserError(msg)
        # 检查模型中字段是否相存在
        for field in rpc_data.field_ids:
            f = self.env['ir.model.fields'].sudo().search([('model_id', '=', model.id), ('name', '=', field.name)])
            if not f:
                msg = u"本地模型:'{}'中字段'{}'不存在,请检查！".format(model_name, field.name)
                logging.info(msg)
                raise UserError(msg)
        return True


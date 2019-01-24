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
        model_name = rpc_data.model_id.model
        # 检查数据存放方式（如果为分开存放，则检查分卡存放的模型和字段是否存在）
        if rpc_data.local_table == '01':
            self.checkout_local_model(rpc_data.local_table_name, rpc_data)
            model_name = rpc_data.local_table_name
        # 开始连接rpc
        model, uid = rpc.connection_rpc(rpc_url, rpc_db, username, password)
        # 组装需要获取的字段和模型名
        fields_dict = self.pack_model_field_to_array(rpc_data)
        logging.info(u"需要获取的字段：{}".format(fields_dict))
        domain = list()
        for d in rpc_data.domain_ids:
            domain.append(rpc.string_transfer_list(d.name))
        logging.info(u"数据表过滤表达式:{}".format(domain))
        result = rpc.search_read(model, rpc_db, uid, password, model_name, domain, fields_dict)
        # 检查模型关联关系
        if rpc_data.connection_relation:
            pk_list = self.solve_the_relationship(model_name, rpc_data, result)
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
        logging.info(u"检查配置的本地模块{}...".format(model_name))
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

    # TODO 未完善项，处理关联关系的函数
    @api.model
    def solve_the_relationship(self, model_name, rpc_data, result):
        """检查关联关系函数，主要是为了解决字段列表中，one2Many、many2One、many2Many字段
        :param model_name: 需要同步的模型名
        :param rpc_data: 需要同步的数据表
        :param result: 获取的rpc结果集
        :return pk_list : 返回关系表主键值
        """
        logging.info(u"检查数据表{}存在的关联关系表单..".format(model_name))
        # 循环本地配置表，获取关联字段dict
        pk_list = list()
        for res in rpc_data.field_ids:
            if res.ttype == 'many2one':
                # 获取对象关系在数据配置表中的主键
                b_data = self.env['rpc.base.data'].search(
                    [('model_name', '=', res.fields_id.relation)])
                if not b_data:
                    raise UserError(
                        u"关系表'{}'在数据同步表中不存在！因此系统无法确定该关系表的主键字段,\r\n请根据系统情况添加'{}'数据表的数据同步规则！".format(
                            res.fields_id.relation, res.fields_id.relation))
                b_data_line = self.env['rpc.base.data.line'].search(
                    [('rpc_id', '=', b_data[0].id), ('primary_key', '=', True)])
                logging.info(u"关系表'{}'的主键为：'{}'".format(res.fields_id.relation, b_data_line[0].name))
                pk_list.append({'model': res.fields_id.relation, 'field': b_data_line[0].name})
        return pk_list

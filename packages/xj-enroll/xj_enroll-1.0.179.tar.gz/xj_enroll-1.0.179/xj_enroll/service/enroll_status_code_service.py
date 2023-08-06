# encoding: utf-8
"""
@project: djangoModel->enroll_status_code_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 报名状态码服务
@created_time: 2022/11/13 16:41
"""
from django.db import transaction

from ..models import Enroll, EnrollRecord, EnrollSubitem, EnrollSubitemRecord
from ..utils.custom_tool import filter_fields_handler, force_transform_type


class EnrollStatusCodeService():
    @staticmethod
    def batch_edit_code(enroll_id: int = None, code: int = None, edit_types: "str|list" = None, exclude_code: int = 124, params: dict = None, **kwargs):
        """
        流程控制，批量修改状态码服务方法
        :param exclude_code: 不查询的该状态code的数据
        :param enroll_id: 报名ID
        :param code: 修改的状态码
        :param edit_types: 需要修改策略列表
        :param params: 需要差异化修改的参数
        :return: data, err
        """
        # ==================== section 参数处理 ================================
        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        if not enroll_id:
            return None, "不是有效的报名ID"

        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="dict", default={})
        params.update(kwargs)

        edit_types = filter_fields_handler(
            input_field_expression=edit_types,
            all_field_list=["enroll", "enroll_record", "enroll_subitem", "enroll_subitem_record"],
            split_char=kwargs.get("split_char", ";")
        )
        code, is_pass = force_transform_type(variable=code, var_type="int")
        exclude_code, is_pass = force_transform_type(variable=exclude_code, var_type="int", default=124)
        # ==================== section 参数处理 ================================

        # ==================== section 开启事务进行修改 start ==================
        sid = transaction.savepoint()
        try:
            # 修改报名主表
            if "enroll" in edit_types:
                enroll_query = Enroll.objects.filter(id=enroll_id)
                if not enroll_query.first():
                    return None, "这是一个不存在的报名ID"
                enroll_query.update(enroll_status_code=code)

            # 修改报名记录
            if "enroll_record" in edit_types:
                enroll_record_query_obj = EnrollRecord.objects
                if exclude_code:
                    enroll_record_query_obj = enroll_record_query_obj.exclude(enroll_status_code=exclude_code)
                if params.get("enroll_record_id"):
                    enroll_record_query_obj = enroll_record_query_obj.filter(id=params["enroll_record_id"])
                else:
                    enroll_record_query_obj = enroll_record_query_obj.filter(enroll_id=enroll_id)
                enroll_record_query_obj.update(enroll_status_code=params.get("enroll_record_code", code))

            # 修改报名分项
            if "enroll_subitem" in edit_types:
                enroll_subitem_query_obj = EnrollSubitem.objects
                if exclude_code:
                    enroll_subitem_query_obj = enroll_subitem_query_obj.exclude(enroll_subitem_status_code=exclude_code)
                if params.get("enroll_subitem_id"):
                    enroll_subitem_query_obj = enroll_subitem_query_obj.filter(id=params["enroll_subitem_id"])
                else:
                    enroll_subitem_query_obj = enroll_subitem_query_obj.filter(enroll_id=enroll_id)
                enroll_subitem_query_obj.update(enroll_subitem_status_code=params.get("enroll_subitem_code", code))

            # 修改报名分项记录
            if "enroll_subitem_record" in edit_types:
                enroll_record_query_obj = EnrollSubitemRecord.objects
                if exclude_code:
                    enroll_record_query_obj = enroll_record_query_obj.exclude(enroll_subitem_status_code=exclude_code)
                if params.get("enroll_subitem_record_id"):
                    enroll_subitem_record_query_obj = enroll_record_query_obj.filter(id=params["enroll_subitem_record_id"])
                else:
                    enroll_subitem_record_query_obj = EnrollSubitemRecord.objects.filter(enroll_record__enroll_id=enroll_id)
                enroll_subitem_record_query_obj.update(enroll_subitem_status_code=params.get("enroll_subitem_record_code", code))

            transaction.clean_savepoints()
            return None, None
            # ==================== section 开启事务进行修改 end ===================
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return None, str(e)

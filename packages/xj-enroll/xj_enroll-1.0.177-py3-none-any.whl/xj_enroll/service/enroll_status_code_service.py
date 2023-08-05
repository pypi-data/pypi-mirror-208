# encoding: utf-8
"""
@project: djangoModel->enroll_status_code_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 报名状态码服务
@created_time: 2022/11/13 16:41
"""
from django.db import transaction
from django.db.models import F

from ..models import Enroll, EnrollRecord, EnrollSubitem, EnrollSubitemRecord


class EnrollStatusCodeService():
    @staticmethod
    def batch_edit_code(enroll_id=None, code=None, edit_types=None, params: dict = None):
        """
        流程控制，批量修改状态码服务方法
        :param enroll_id: 报名ID
        :param code: 修改的状态码
        :param edit_types: 需要修改策略列表
        :param params: 需要差异化修改的参数
        :return: data, err
        """
        if edit_types is None:
            edit_types = ["enroll", "enroll_record", "enroll_subitem", "enroll_subitem_record"]
        edit_types = edit_types.split(";") if isinstance(edit_types, str) else edit_types

        # 开启事务进行修改
        sid = transaction.savepoint()
        try:
            if "enroll" in edit_types:
                enroll_query_obj = Enroll.objects.filter(id=enroll_id)
                enroll_query_obj.update(enroll_status_code=code)

            if "enroll_record" in edit_types:
                enroll_record_code = params.get("enroll_record_code") or code
                if params.get("enroll_record_id"):
                    enroll_record_query_obj = EnrollRecord.objects.filter(id=params["enroll_record_id"]).exclude(enroll_status_code=124)
                    enroll_record_query_obj.update(enroll_status_code=enroll_record_code)
                else:
                    enroll_record_query_obj = EnrollRecord.objects.filter(enroll_id=enroll_id).exclude(enroll_status_code=124)
                    enroll_record_query_obj.update(enroll_status_code=enroll_record_code)

            if "enroll_subitem" in edit_types:
                enroll_subitem_code = params.get("enroll_subitem_code") or code
                if params.get("enroll_subitem_id"):
                    enroll_record_query_obj = EnrollRecord.objects.filter(id=params["enroll_subitem_id"]).exclude(enroll_status_code=124)
                    enroll_record_query_obj.update(enroll_status_code=enroll_subitem_code)
                else:
                    enroll_subitem_query_obj = EnrollSubitem.objects.filter(enroll_id=enroll_id).exclude(enroll_subitem_status_code=124)
                    enroll_subitem_query_obj.update(enroll_subitem_status_code=enroll_subitem_code)

            if "enroll_subitem_record" in edit_types:
                enroll_subitem_record_code = params.get("enroll_subitem_record_code") or code
                if params.get("enroll_subitem_record_id"):
                    enroll_record_query_obj = EnrollRecord.objects.filter(id=params["enroll_subitem_record_id"]).exclude(enroll_status_code=124)
                    enroll_record_query_obj.update(enroll_status_code=enroll_subitem_record_code)
                else:
                    enroll_subitem_record_query_obj = EnrollSubitemRecord.objects.annotate(enroll_id=F("enroll_record__enroll_id")) \
                        .filter(enroll_id=enroll_id).exclude(enroll_subitem_status_code=124)
                    enroll_subitem_record_query_obj.update(enroll_subitem_status_code=enroll_subitem_record_code)
            transaction.clean_savepoints()

            return None, None
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return None, str(e)

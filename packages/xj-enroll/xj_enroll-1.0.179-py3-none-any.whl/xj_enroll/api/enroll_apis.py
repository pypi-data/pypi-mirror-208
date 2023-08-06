from django.db import transaction
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from xj_thread.services.thread_category_service import ThreadCategoryService
from xj_thread.services.thread_category_tree_service import ThreadCategoryTreeServices
from xj_thread.services.thread_item_service import ThreadItemService
from xj_thread.services.thread_list_service import ThreadListService
from xj_user.services.user_detail_info_service import DetailInfoService
from xj_user.utils.user_wrapper import user_authentication_force_wrapper, user_authentication_wrapper
from ..service.enroll_services import EnrollServices
from ..service.rule_service import RuleValueService
from ..service.subitem_service import SubitemService
from ..utils.custom_response import util_response
from ..utils.custom_tool import parse_data, format_params_handle, request_params_wrapper, filter_result_field, flow_service_wrapper, write_to_log, filter_fields_handler, format_list_handle, \
    force_transform_type
from ..utils.join_list import JoinList


class EnrollAPI(APIView):
    @staticmethod
    def list_handle(*args, request_params=None, user_info=None, **kwargs, ):
        """
        接口执行手柄，对外暴露，可使用路程调用
        :param request_params: request请求的参数
        :param user_info: 请求的用户信息
        :return: data, err
        """
        if request_params is None:
            request_params = {}
        filter_fields = request_params.get("filter_fields", None)
        # ================== 信息id列表反查询报名 start===============================
        thread_params = format_params_handle(
            param_dict=request_params,
            filter_filed_list=["title", "subtitle", "access_level", "author"],
            is_remove_empty=True
        )
        if thread_params:
            thread_ids, err = ThreadListService.search_ids(search_prams=thread_params)
            if not err:
                request_params["thread_id_list"] = thread_ids
        # ================== 信息id列表反查询报名 end  ===============================

        # ================== 根据平台编码获取类别ID列表进行反查 start===============================
        platform_code = request_params.pop("platform_code", None)
        if platform_code:
            id_list, err = ThreadCategoryService.list(
                params={"platform_code": platform_code},
                filter_fields="id",
                need_pagination=False
            )
            if not err:
                request_params["category_id_list"] = [i["id"] for i in id_list]
        # ================== 根据平台编码获取类别ID列表 end  ===============================

        # ================== 查询当前类别的所有子类别 start===============================
        need_category_child, is_pass = force_transform_type(variable=request_params.pop("need_category_child", None), var_type="bool", default=False)
        if need_category_child and (request_params.get("category_id", None) or request_params.get("category_value", None)):
            id_list, err = ThreadCategoryTreeServices.get_child_ids(
                category_id=request_params.pop("category_id", None),
                category_value=request_params.pop("category_value", None)
            )
            if not err:
                request_params["category_id_list"] = id_list
        # ================== 查询当前类别的所有子类别 end  ===============================
        # 报名列表搜索
        data, err = EnrollServices.enroll_list(
            params=request_params,
            filter_fields=filter_fields
        )
        if err:
            return None, err

        # ================== 合并信息表数据 start===============================
        id_list = [i['thread_id'] for i in data['list'] if i]
        thread_list, err = ThreadListService.search(id_list)
        data['list'] = JoinList(data['list'], thread_list, "thread_id", "id").join()
        # 用户信息合并
        user_id_list = list(set([i['user_id'] for i in data['list'] if i]))
        user_info_list = DetailInfoService.get_list_detail(user_id_list=user_id_list, filter_fields=filter_fields or ["user_id", "real_name", "full_name", "nickname"])
        JoinList(data['list'], user_info_list, "user_id", "user_id").join()
        # 小数点四舍五入
        for i in data['list']:
            i["price"] = round(i["price"], 2)
        # ================== 合并信息表数据 end  ===============================

        # ================== 字段过滤 start  ===============================
        # 返回字段处理，支持加减法原则、列表全全部匹配原则
        try:
            # 获取所有的key
            default_field_list = []
            for i in data['list']:
                default_field_list.extend(list(i.keys()))
            # 过滤字段
            filter_fields = filter_fields_handler(
                input_field_expression=request_params.get("filter_fields", None),
                default_field_list=list(set(default_field_list))
            )
        except Exception as e:
            filter_fields = None
        data["list"] = filter_result_field(result_list=data["list"], filter_filed_list=filter_fields)
        # ================== 字段过滤 end    ===============================
        # 数据返回
        if err:
            return None, err
        return data, None

    @api_view(['GET'])
    @request_params_wrapper
    @user_authentication_wrapper
    def list(self, *args, request_params=None, user_info=None, **kwargs, ):
        data, err = EnrollAPI.list_handle(request_params=request_params, user_info=user_info, )
        # 数据返回
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @api_view(['POST', ])
    @user_authentication_force_wrapper
    @request_params_wrapper
    @flow_service_wrapper
    def add(self, *args, user_info, request_params, **kwargs, ):
        # ============   字段验证处理 start ============
        request_params.setdefault("user_id", user_info.get("user_id", None))  # 用户ID
        request_params.setdefault("subitems", [])  # 报名分项
        enroll_subitem_status_code = request_params.pop("enroll_subitem_status_code", 242)  # 报名分项 状态码

        # ============   绑定计价分组ID start ============
        try:
            if not request_params.get("enroll_rule_group_id"):
                category_id = request_params.get("category_id", None)
                classify_id = request_params.get("classify_id", None)
                assert category_id and classify_id, "category_id，classify_id必填"
                res, err = RuleValueService.group_list({"category_id": category_id, "classify_id": classify_id})
                assert not err, err
                assert res, "没有找到对应的计价规则组ID"
                request_params.setdefault("enroll_rule_group_id", res[0].get("id"))
        except Exception as e:
            write_to_log(prefix="报名发布，绑定计价组ID异常", err_obj=e)
        # ============   绑定计价分组ID end ============

        # ============ 信息表添加  start ============
        sid = transaction.savepoint()
        request_params["has_enroll"] = 1  # 默认参数开启报名
        if not request_params.get("thread_id"):
            data, err = ThreadItemService.add(request_params)
        else:
            data, err = ThreadItemService.edit(request_params, request_params.get("thread_id"))
        if err:
            transaction.savepoint_rollback(sid)
            return util_response(err=1002, msg="信息添加错误：" + err)
        # ============ 信息表添加  end   ============

        # ============ 报名主表添加  start ============
        thread_id = request_params.get("thread_id", data.get("id", None))
        request_params.setdefault("thread_id", thread_id)
        main_instance, err = EnrollServices.enroll_add(params=request_params)
        if err:
            transaction.savepoint_rollback(sid)
            return util_response(err=1003, msg=err)
        # ============ 报名主表添加  end ============

        # ============ 报名分项添加  start ============
        for item_params in request_params.pop("subitems", []):
            item_params.setdefault("enroll_id", main_instance.get('id'))
            item_params.setdefault("enroll_subitem_status_code", enroll_subitem_status_code)
            data, err = SubitemService.add(item_params)
            if err:
                transaction.savepoint_rollback(sid)
                return util_response(err=1004, msg=err)
        # ============ 报名分项添加  end ============

        transaction.clean_savepoints()  # 清除保存点
        return util_response(data=main_instance)

    @api_view(['GET', 'POST', ])
    @user_authentication_force_wrapper
    @request_params_wrapper
    def detail(self, *args, user_info=None, request_params=None, **kwargs):
        # 参数验证
        if request_params is None:
            request_params = {}
        if user_info is None:
            user_info = {}

        params = request_params
        enroll_id = kwargs.get("enroll_id", None) or params.pop("enroll_id", None)
        if not enroll_id:
            return util_response(err=1000, msg="参数错误:enroll_id不可以为空")

        user_id = user_info.get("user_id", None)

        # 获取报名详情
        data, err = EnrollServices.enroll_detail(enroll_id, user_id=user_id)
        if err:
            return util_response(err=1001, msg=err)

        # 用户数据拼接
        push_user_info, user_err = DetailInfoService.get_detail(user_id=user_id)
        if push_user_info:
            data.update(push_user_info)

        # 信息表 数据拼接
        thread_list, err = ThreadListService.search([data.get("thread_id")])
        if err:
            return util_response(err=1002, msg=err)
        data = JoinList([data], thread_list, "thread_id", "id").join()
        data = data[0] if not len(data) > 1 else data
        data["price"] = round(data["price"] or 0, 2)

        # 字段过滤
        filter_fields = filter_fields_handler(
            input_field_expression=params.get("filter_fields", None),
            default_field_list=format_list_handle(
                param_list=list(data.keys()) if data and isinstance(data, dict) else None,
                remove_filed_list=[
                    "real_name", "sex", "birth", "tags", "signature", "avatar", "cover", "language", "more",
                    "id_card_front", "id_card_back", "real_name_is_pass", "id_card",
                    "certificate", "work experience", "qualification_certificate", "audit_status",
                    "score", "user_name", "phone", "email", "register_time",
                    "user_info", "wechat_openid", "is_deleted",
                ]
            )
        )
        data = format_params_handle(data, filter_filed_list=filter_fields, is_remove_null=False)
        # 响应数据
        if err:
            return util_response(err=1003, msg=err)
        return util_response(data=data)

    @api_view(['POST', 'PUT'])
    @request_params_wrapper
    @flow_service_wrapper
    def edit(self, *args, request_params=None, **kwargs):
        # 参数处理
        request_params, is_pass = force_transform_type(variable=request_params, var_type="dict", default={})
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="dict", default={})
        enroll_id = kwargs.get("enroll_id") or request_params.pop("enroll_id", None) or request_params.pop("id", None)
        if not enroll_id:
            return util_response(err=1000, msg="参数错误:不是一个有效的报名ID")

        # 报名表修改
        instance, err = EnrollServices.enroll_edit(request_params.copy(), enroll_id)
        if err:
            return util_response(err=1001, msg=err)

        # 信息表修改
        thread_id = request_params.pop("thread_id", None) or instance.get("thread_id", None)
        if thread_id:
            data, err = ThreadItemService.edit(request_params.copy(), thread_id)
            if err:
                return util_response(err=1002, msg=err)
        return util_response(data=instance)

    @require_http_methods(['DELETE'])
    def delete(self, *args, **kwargs, ):
        params = parse_data(self)
        enroll_id = kwargs.get("enroll_id") or params.pop("enroll_id") or None
        if not enroll_id:
            return util_response(err=1000, msg="参数错误:enroll_id不可以为空")
        data, err = EnrollServices.enroll_delete(enroll_id)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @require_http_methods(['GET'])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def own_list(self, *args, request_params=None, user_info=None, **kwargs):
        """分页查看本人的发布的报名信息列表"""
        thread_params = format_params_handle(
            param_dict=request_params,
            filter_filed_list=[
                "user_id", "title", "subtitle", "summary", "access_level", "author", "has_enroll", "has_fee", "has_comment", "has_location", "is_original",
            ]
        )
        if thread_params:
            thread_ids, err = ThreadListService.search_ids(thread_params)
            request_params["thread_id_list"] = thread_ids if not err else []

        filter_fields = request_params.pop("filter_fields", None)
        request_params["user_id"] = user_info.get("user_id")
        need_pagination = request_params.pop("need_pagination", 1)
        need_pagination = int(need_pagination)
        data, err = EnrollServices.enroll_own_list(request_params, need_pagination=need_pagination)
        if err:
            return util_response(err=1000, msg=err)
        # 合并thread模块数据
        id_list = [i['thread_id'] for i in data['list'] if i]
        thread_list, err = ThreadListService.search(id_list)
        data['list'] = JoinList(data['list'], thread_list, "thread_id", "id").join()

        filter_fields = filter_fields.split(";") if filter_fields else None
        data["list"] = filter_result_field(result_list=data["list"], filter_filed_list=filter_fields)
        # 数据返回
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @api_view(['GET', 'POST', ])
    @request_params_wrapper
    @user_authentication_force_wrapper
    def undertake_list(self, *args, request_params=None, user_info=None, **kwargs):
        """工作人员查看自己的报名记录列表"""
        filter_fields = request_params.get("filter_fields", None)
        request_params["user_id"] = user_info.get("user_id")
        need_pagination = request_params.pop("need_pagination", 1)
        need_pagination = int(need_pagination)
        # 信息表
        thread_params = format_params_handle(
            param_dict=request_params,
            filter_filed_list=[
                "title", "subtitle", "access_level", "author", "has_enroll", "has_fee", "has_comment",
                "has_location", "is_original",
            ]
        )
        if thread_params:
            thread_ids, err = ThreadListService.search_ids(thread_params)
            request_params["thread_id_list"] = thread_ids if not err else []
        data, err = EnrollServices.enroll_undertake_list(request_params, need_pagination=need_pagination)
        if err:
            return util_response(err=1000, msg=err)
        # 分页数据
        if need_pagination:
            for i in data["list"]:
                i['price'] = round(float(i["price"]), 2)
                i['main_amount'] = round(float(i["main_amount"]), 2)
                i['coupon_amount'] = round(float(i["coupon_amount"]), 2)
                i['again_reduction'] = round(float(i["again_reduction"]), 2)
                i['subitems_amount'] = round(float(i["subitems_amount"]), 2)
                i['deposit_amount'] = round(float(i["deposit_amount"]), 2)
                i['amount'] = round(float(i["amount"]), 2)
                i['paid_amount'] = round(float(i["paid_amount"]), 2)
                i['unpaid_amount'] = round(float(i["unpaid_amount"]), 2)
                i['fee'] = round(float(i["fee"]), 2)

            # 合并thread模块数据
            id_list = [i['thread_id'] for i in data['list'] if i]
            thread_list, err = ThreadListService.search(id_list)
            data['list'] = JoinList(data['list'], thread_list, "thread_id", "id").join()

            filter_fields = filter_fields.split(";") if filter_fields else None
            data["list"] = filter_result_field(result_list=data["list"], filter_filed_list=filter_fields)
            # 数据返回
            if err:
                return util_response(err=1001, msg=err)
            return util_response(data=data)
        else:
            for i in data:
                i['price'] = round(float(i["price"]), 2)
                i['main_amount'] = round(float(i["main_amount"]), 2)
                i['coupon_amount'] = round(float(i["coupon_amount"]), 2)
                i['again_reduction'] = round(float(i["again_reduction"]), 2)
                i['subitems_amount'] = round(float(i["subitems_amount"]), 2)
                i['deposit_amount'] = round(float(i["deposit_amount"]), 2)
                i['amount'] = round(float(i["amount"]), 2)
                i['paid_amount'] = round(float(i["paid_amount"]), 2)
                i['unpaid_amount'] = round(float(i["unpaid_amount"]), 2)
                i['fee'] = round(float(i["fee"]), 2)

            # 合并thread模块数据
            id_list = [i['thread_id'] for i in data if i]
            thread_list, err = ThreadListService.search(id_list)
            data = JoinList(data, thread_list, "thread_id", "id").join()

            filter_fields = filter_fields.split(";") if filter_fields else None
            data = filter_result_field(result_list=data, filter_filed_list=filter_fields)
            # 数据返回
            if err:
                return util_response(err=1001, msg=err)
            return util_response(data=data)

    @api_view(['GET'])
    @request_params_wrapper
    def enroll_pay_callback(self, *args, request_params=None, **kwargs):
        # 用户id获取
        order_no = request_params.get("order_no", None)
        if not order_no:
            return util_response(err=1000, msg="order_no 不能为空")

        data, err = EnrollServices.bxtx_pay_call_back(order_no)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(msg="回调成功")

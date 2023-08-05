# encoding: utf-8
"""
@project: djangoModel->enroll_status_code
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 所有状态相关操作接口
@created_time: 2022/11/13 16:31
"""
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from xj_user.utils.user_wrapper import user_authentication_force_wrapper
from ..service.enroll_status_code_service import EnrollStatusCodeService
from ..utils.custom_response import util_response
from ..utils.custom_tool import request_params_wrapper, flow_service_wrapper, force_transform_type, dynamic_load_class, write_to_log


class EnrollStatusCodeAPI(APIView):
    @require_http_methods(['PUT'])
    @user_authentication_force_wrapper
    @request_params_wrapper
    @flow_service_wrapper
    def batch_edit_code(self, *args, request_params=None, user_info=None, **kwargs, ):
        code = request_params.pop("code", None)
        if not code:
            return util_response(err=1000, msg="参数错误，code|enroll_id 不能为空")
        enroll_id = request_params.pop("enroll_id", None) or kwargs.get("enroll_id", None)
        edit_types = request_params.pop("edit_types", None)
        data, err = EnrollStatusCodeService.batch_edit_code(
            enroll_id=enroll_id,
            code=code,
            edit_types=edit_types,
            params=request_params
        )
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @require_http_methods(['GET'])
    @user_authentication_force_wrapper
    @request_params_wrapper
    @flow_service_wrapper
    def ask_pay_status(self, *args, request_params=None, user_info=None, **kwargs, ):
        # 参数处理
        # print("request_params:", request_params)
        success_code = request_params.get("success_code", )
        fail_code = request_params.get("fail_code")
        edit_types = request_params.get("edit_types", "enroll;enroll_record;enroll_subitem;enroll_subitem_record")
        enroll_id, is_pass = force_transform_type(variable=request_params.get("enroll_id"), var_type="int")
        if not enroll_id:
            return util_response(err=1000, msg="msg:参数错误，报名ID不能为空:tip:非法请求")
        if not success_code or not fail_code:
            return util_response(err=1001, msg="msg:请检亲求参数，或者检查流程配置:tip:非法请求")

        # note 询问资金模块是完成了订单 得到 WATING(等待中),SUCCESS（支付成功）,FAIL（支付失败）三种状态
        PaymentService, import_err = dynamic_load_class(import_path="xj_payment.services.payment_service", class_name="PaymentService")
        if import_err:
            return util_response(err=1002, msg="该系统并没有安装支付模块")

        try:
            order_info, err = PaymentService.ask_order_status(params={
                "enroll_id": enroll_id
            })
            if err:
                pay_status = "FAIL"
            else:
                pay_status = order_info.get("status", "FAIL")

        except Exception as e:
            write_to_log(prefix="订单支付的状态查询异常", err_obj=e)
            return util_response(err=1004, msg="订单支付的状态查询异常请查看详细日志")

        if pay_status == "WATING":
            return util_response(msg="msg:正在支付中;tip:正在支付中", data=pay_status)
        elif pay_status == "SUCCESS":
            code = success_code
        elif pay_status == "FAIL":
            code = fail_code
        else:
            return util_response(msg="msg:支付模块异常，并没有给到支付状态;tip:正在支付中", data=pay_status)

        # 修改报名的全部状态
        data, err = EnrollStatusCodeService.batch_edit_code(
            enroll_id=enroll_id,
            code=code,
            edit_types=edit_types.split("edit_types"),
            params=request_params
        )
        if err:
            return util_response(err=1005, msg=err)
        return util_response(data=data)

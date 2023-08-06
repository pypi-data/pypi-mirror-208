# encoding: utf-8
"""
@project: djangoModel->service_register
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 对外开放服务调用注册白名单
@created_time: 2023/1/12 14:29
"""

import xj_enroll
from xj_enroll.service import subitem_service, enroll_subitem_record_service, enroll_record_serivce, enroll_status_code_service
from .service import enroll_services

# 对外服务白名单
register_list = [
    {
        # 报名添加
        "service_name": "enroll_add",
        "pointer": enroll_services.EnrollServices.enroll_add
    },
    {
        # 报名修改
        "service_name": "enroll_edit",
        "pointer": enroll_services.EnrollServices.enroll_edit
    },
    {
        # 镖师报名
        "service_name": "record_add",
        "pointer": enroll_record_serivce.EnrollRecordServices.record_add
    },
    {
        # 用户指派镖师
        "service_name": "appoint",
        "pointer": enroll_record_serivce.EnrollRecordServices.appoint
    },
    {
        # 报名记录修改
        "service_name": "record_edit",
        "pointer": enroll_record_serivce.EnrollRecordServices.record_edit
    },
    {
        # 报名记录修改
        "service_name": "subitem_record_edit",
        "pointer": enroll_subitem_record_service.EnrollSubitemRecordService.edit
    },
    {
        # 报名记录修改
        "service_name": "subitem_edit",
        "pointer": subitem_service.SubitemService.edit
    },
    {
        # 批量修改状态码
        "service_name": "batch_edit_code",
        "pointer": enroll_status_code_service.EnrollStatusCodeService.batch_edit_code
    },
    {
        # 批余额验收联动
        "service_name": "enroll_check_and_accept",
        "pointer": enroll_services.EnrollServices.enroll_check_and_accept
    },
    {
        # 老版本业务逻辑兼容，批余额验收联动
        "service_name": "old_enroll_check_and_accept",
        "pointer": enroll_services.EnrollServices.old_enroll_check_and_accept
    },

]


# 遍历注册
def register():
    for i in register_list:
        setattr(xj_enroll, i["service_name"], i["pointer"])


if __name__ == '__main__':
    register()

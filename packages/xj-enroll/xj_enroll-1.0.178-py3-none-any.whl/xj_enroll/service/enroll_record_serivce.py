# encoding: utf-8
"""
@project: djangoModel->enroll_record_serivce
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户报名记录
@created_time: 2022/9/17 15:45
"""
from django.core.paginator import Paginator, EmptyPage
from django.db.models import F

from xj_thread.services.thread_item_service import ThreadItemService
from xj_thread.services.thread_list_service import ThreadListService
from xj_user.services.user_detail_info_service import DetailInfoService
from ..models import EnrollRecord, Enroll, EnrollSubitemRecord, EnrollRecordExtendField, EnrollSubitem
from ..serializers import EnrollRecordListSerializer, EnrollRecordListV2Serializer
from ..service.enroll_status_code_service import EnrollStatusCodeService
from ..service.enroll_subitem_record_service import EnrollSubitemRecordService
from ..service.valuation_service import ValuationService
from ..utils.custom_tool import format_params_handle, filter_result_field, write_to_log, force_transform_type, filter_fields_handler
from ..utils.join_list import JoinList


class EnrollRecordServices:
    enroll_record_fields = [i.name for i in EnrollRecord._meta.fields]
    enroll_record_extend_fields = [i.name for i in EnrollRecord._meta.fields if "field_" in i.name]
    enroll_record_except_extend_fields = [i.name for i in EnrollRecord._meta.fields if not "field_" in i.name]
    enroll_record_validate_type_fields = [
        "id|int", "enroll_id|int", "apply_subitem_ids|list", "user_id|int", "enroll_auth_status", "enroll_pay_status",
        "enroll_status_code|int", "create_time|date", "price|float", "deposit|float", "count|int", "main_amount|float",
        "coupon_amount|float", "again_reduction|float", "subitems_amount|float", "deposit_amount|float", "amount|float",
        "paid_amount|float", "unpaid_amount|float", "fee|float", "photos|dict", "files|dict", "score|float", "reply",
        "remark", "finish_time|date", "again_price|float", "again_fee|float", "initiator_again_price|float",
        "estimated_time|date", "update_time|date",
        "thread_id_list|list_int",
        "enroll_id_list|list_int",
        "enroll_status_code_list|list_int",
    ]

    @staticmethod
    def extend_transform_fields(result_list: list = None):
        """
        报名记录列表的扩展字段替换过滤
        :param result_list:
        :return: result_list
        """
        filed_map_list = list(EnrollRecordExtendField.objects.all().values("field", 'field_index'))
        filed_map = {item['field_index']: item['field'] for item in filed_map_list}

        # 扩展字段替换，并过滤
        enroll_record_list = filter_result_field(
            result_list=result_list,
            alias_dict=filed_map
        )
        enroll_record_list = filter_result_field(
            result_list=enroll_record_list,
            remove_filed_list=["field_1", "field_2", "field_3", "field_4", "field_5", "field_6", "field_7", "field_8", "field_9", "field_10"]
        )
        return enroll_record_list

    @staticmethod
    def check_can_add(enroll_id: int = None, user_id: int = None, apply_subitem_ids: list = None, **kwargs):
        """
        判断是否可以报名
        :param apply_subitem_ids: 期待申请分项ID列表
        :param enroll_id: 报名ID
        :param user_id: 用户ID
        :return: Bool
        """

        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        user_id, is_pass = force_transform_type(variable=user_id, var_type="int")
        if not enroll_id or not user_id:
            return None, "参数错误"

        # 状态码常量
        draft_code, is_pass = force_transform_type(variable=kwargs.get("draft_code", 124), var_type="int", default=124)  # 草稿code
        enrolled_code, is_pass = force_transform_type(variable=kwargs.get("enrolled_code", 356), var_type="int", default=356)  # 已报名code
        enrolling_code, is_pass = force_transform_type(variable=kwargs.get("enrolling_code", 234), var_type="int", default=234)  # 报名中code

        # 判断报名ID是否正确
        enroll_obj = Enroll.objects.filter(id=enroll_id, enroll_status_code=enrolling_code).first()
        if not enroll_obj:
            return False, "当前报名项不可报名"

        # 当前用户报名过了，不允许报名了
        enroll_record_obj = EnrollRecord.objects.filter(enroll_id=enroll_id).exclude(enroll_status_code=draft_code)  # 拿到搜索报名记录
        this_user_record_obj = enroll_record_obj.filter(user_id=user_id).first()
        if this_user_record_obj:
            return False, "已经报名，无需再次报名"

        # 报名分项ID列表
        apply_subitem_ids, is_pass = force_transform_type(variable=apply_subitem_ids, var_type="list_int")
        if not apply_subitem_ids:
            return True, None
        enroll_subitem_ids = list(EnrollSubitem.objects.filter(enroll_id=enroll_id).values("id"))
        enroll_subitem_ids = [i.get("id") for i in enroll_subitem_ids]
        for apply_subitem_id in apply_subitem_ids:
            if not apply_subitem_id in enroll_subitem_ids:
                return False, "您期望报名的分项中存在无效的分项,请重新选择您期望报名的分项"
        return True, None

    @staticmethod
    def check_can_cancel(pk, change_code=None, should_code=None):
        """
        检查报名记录是否可以修改为草稿
        :param pk: 主键ID
        :return: data, err
        """
        if change_code and should_code and str(change_code) == "124":
            current_status_code = EnrollRecord.objects.filter(id=pk).values("enroll_status_code").first()
            current_status_code = current_status_code.get("enroll_status_code", 0)
            if str(should_code) == str(current_status_code):
                return True, None
            else:
                return False, None

        return True, None

    @staticmethod
    def record_add(params):
        """
        报名添加
        :param params: request解析出来的json参数
        :return: 报名记录json
        """
        # 判断是否可以继续报名
        enroll_id = params.get("enroll_id")
        user_id = params.get("user_id")
        apply_subitem_ids = params.get("apply_subitem_ids", None)
        if not enroll_id:
            return None, "enroll_id不能为空"

        # 查看是否符合报名条件
        res, err_msg = EnrollRecordServices.check_can_add(enroll_id, user_id, apply_subitem_ids)
        if not res:
            return None, err_msg

        filed_map_list = list(EnrollRecordExtendField.objects.all().values("field", 'field_index'))
        reversal_filed_map = {item['field']: item['field_index'] for item in filed_map_list if item['field_index'] in EnrollRecordServices.enroll_record_extend_fields}
        # 修改内容检查处理
        try:
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                alias_dict=reversal_filed_map,
                is_remove_empty=True,
                filter_filed_list=list(reversal_filed_map.keys()) + [
                    "enroll_id|int",
                    "apply_subitem_ids|list_int",
                    "user_id|int",
                    "enroll_auth_status|int",
                    "enroll_pay_status|int",
                    "enroll_status_code|int",
                    "create_time|date",
                    "price|float",
                    "deposit|float",
                    "count|int",
                    "main_amount|float",
                    "coupon_amount|float",
                    "again_reduction|float",
                    "subitems_amount|float",
                    "deposit_amount|float",
                    "amount|float",
                    "paid_amount|float",
                    "unpaid_amount|float",
                    "fee|float",
                    "photos|json",
                    "files|json",
                    "score|float",
                    "reply",
                    "remark",
                    "finish_time|date",
                    "again_price|float",
                    "again_fee|float",
                    "initiator_again_price|float",
                    "estimated_time|date",
                    "update_time|date",
                ],
            )
        except ValueError as e:
            return None, str(e)

        # 必填字段验证
        must_keys = ["enroll_id", "user_id"]
        for i in must_keys:
            if not params.get(i):
                return None, str(i) + "为必填"

        # 字段过滤
        try:
            instance = EnrollRecord.objects.create(**params)
        except Exception as e:
            return None, str(e)
        return instance.to_json(), None

    @staticmethod
    def record_list(params: dict, need_pagination: bool = True, exclude_code=124, **kwargs):
        """
        查询报名记录列表
        :param exclude_code: 不查看某状态码（enroll_status_code）
        :param params: 查询参数
        :param need_pagination: 是否分页
        :return: 报名记录
        """
        page, is_pass = force_transform_type(variable=params.pop('page', 1), var_type="int", default=1)
        size, is_pass = force_transform_type(variable=params.pop('size', 10), var_type="int", default=10)
        # ============= section 根据信息搜索信息ID列表来检索报名记录 ===========================
        thread_search_prams = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "title", "subtitle", "access_level", "author",
                "has_enroll", "has_fee", "has_comment", "has_location", "is_original", "finance_invoicing_code",
                "category_value", "classify_value", "thread_category_value", "thread_classify_value",
                "platform_code", "need_auth", "show_value"
            ],
        )
        if thread_search_prams:
            params["thread_id_list"], err = ThreadListService.search_ids(thread_search_prams, is_strict_mode=False)
        # ============= section 根据信息搜索信息ID列表来检索报名记录 ===========================

        # ============= section 扩展字段映射获取，扩展字段查询前 筛选替换 start ===========================
        filed_map_list = list(EnrollRecordExtendField.objects.all().values("field", 'field_index'))
        filed_map = {item['field_index']: item['field'] for item in filed_map_list}
        reversal_filed_map = {item['field']: item['field_index'] for item in filed_map_list}

        # 添加构建ORM的查询参数
        reversal_filed_map.update({
            "category_id": "enroll__category_id",
            "enroll_user_id": "enroll__user_id",
            "thread_id": "enroll__thread_id",
            "enroll": "enroll_id",
            "enroll_id": "enroll_id",
            "thread_id_list": "enroll__thread_id__in",
            "enroll_id_list": "enroll_id__in",
            "enroll_status_code_list": "enroll_status_code__in"
        })

        params = format_params_handle(
            param_dict=params,
            filter_filed_list=list(reversal_filed_map.keys()) + EnrollRecordServices.enroll_record_validate_type_fields,
            split_list=["enroll_status_code_list", "enroll_id_list", "thread_id_list"],
            alias_dict=reversal_filed_map
        )
        # ============= section 扩展字段映射获取，扩展字段查询前 筛选替换 end    ===========================

        # ==================== section 构建ORM条件查询 start===============================
        record_obj = EnrollRecord.objects.annotate(thread_id=F("enroll__thread_id")).filter(**params)
        exclude_code, is_pass = force_transform_type(variable=exclude_code, var_type="int")
        if exclude_code:
            record_obj = record_obj.exclude(enroll_status_code=124)
        total = record_obj.count()
        if not need_pagination:
            enroll_list = EnrollRecordListSerializer(record_obj, many=True).data
        else:
            paginator = Paginator(record_obj, size)
            try:
                record_obj = paginator.page(page)
            except EmptyPage:
                record_obj = paginator.page(paginator.num_pages)
            enroll_list = EnrollRecordListSerializer(record_obj, many=True).data
        # ==================== section 构建ORM条件查询 end   ===============================

        # 扩展字段替换，并过滤没有配置扩展字段
        enroll_list = filter_result_field(
            result_list=filter_result_field(
                result_list=enroll_list,
                alias_dict=filed_map  # 替换已经配置的扩展字段
            ),
            remove_filed_list=EnrollRecordServices.enroll_record_extend_fields  # 去掉没有配置的扩展字段
        )

        # ==================== 拼接跨服务获取信息 start===============================
        try:
            # 拼接用户信息
            user_info_list = DetailInfoService.get_list_detail(
                None,
                user_id_list=[i["user_id"] for i in enroll_list if i.get("user_id")],
                filter_fields=["user_id", "real_name", "user_name", "full_name", "nickname", "phone"]
            )
            JoinList(enroll_list, user_info_list, l_key="user_id", r_key="user_id").join()

            # 拼接Thread信息
            thread_list, err = ThreadListService.search(
                id_list=[i["thread_id"] for i in enroll_list if i.get("thread_id")],
                filter_fields=["id", "title", "subtitle", "summary", "author"]
            )
            JoinList(enroll_list, thread_list, l_key="thread_id", r_key="id").join()
        except Exception as e:
            write_to_log(prefix="报名记录列表服务拼接数据异常", err_obj=e)
        # ==================== 拼接跨服务获取信息 end   ===============================

        # 返回数据
        return enroll_list if not need_pagination else {'total': total, "page": page, "size": size, 'list': enroll_list}, None

    # note 服务即将被 上面的record_list代替
    @staticmethod
    def complex_record_list(params: dict = None):
        """
        这个接口仅仅提供API使用,不提供服务调用，关联太多的数据，使用了很多的where_in,所以限制分页
        :param params:
        :param need_pagination:
        :return:
        """
        # 参数预处理
        params, is_pass = force_transform_type(variable=params, var_type="int", default={})
        page, is_pass = force_transform_type(variable=params.pop('page', 1), var_type="int", default=1)
        size, is_pass = force_transform_type(variable=params.pop('size', 10), var_type="int", default=10)
        if size > 100:
            return None, "分布不可以超过100页"
        # 根据信息搜索信息ID列表来检索报名记录
        thread_search_prams = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "title", "subtitle", "access_level", "author",
                "has_enroll", "has_fee", "has_comment", "has_location", "is_original", "finance_invoicing_code",
                "category_value", "classify_value", "thread_category_value", "thread_classify_value",
                "platform_code", "need_auth", "show_value"
            ],
        )
        if thread_search_prams:
            params["thread_id_list"], err = ThreadListService.search_ids(thread_search_prams, is_strict_mode=False)

        # 扩展字段映射获取
        filed_map_list = list(EnrollRecordExtendField.objects.all().values("field", 'field_index'))
        forward_filed_map = {item['field_index']: item['field'] for item in filed_map_list}
        reversal_filed_map = {item['field']: item['field_index'] for item in filed_map_list}
        filter_filed_list = list(forward_filed_map.values()) + [
            "thread_id_list", "id", "category_id", "enroll_id", "user_id", "enroll_auth_status_id", "enroll_pay_status_id", "enroll_status_code", "create_time",
            "price", "deposit", "count", "main_amount", "coupon_amount", "again_reduction", "subitems_amount", "deposit_amount", "amount",
            "paid_amount", "unpaid_amount", "fee", "photos", "files", "score", "reply", "remark", "finish_time",
            "again_price", "again_fee", "initiator_again_price", "estimated_time", "update_time",
        ]
        reversal_filed_map.update({
            "thread_id_list": "enroll__thread_id__in",
            "category_id": "enroll__category_id",
            "enroll": "enroll_id"
        })

        # 扩展字段搜索项筛选
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=filter_filed_list,
            alias_dict=reversal_filed_map
        )
        # PS 124状态码任务取消报名，不予显示
        enroll_obj = EnrollRecord.objects.filter(**params).annotate(
            thread_id=F("enroll__thread_id"),
            enroll_user_id=F("enroll__user_id"),
        ).exclude(enroll_status_code=124)
        count = enroll_obj.count()

        # 是否分页
        paginator = Paginator(enroll_obj, size)
        try:
            enroll_obj = paginator.page(page)
        except EmptyPage:
            enroll_obj = paginator.page(paginator.num_pages)
        enroll_list = EnrollRecordListV2Serializer(enroll_obj, many=True).data

        # 扩展字段替换，并过滤
        enroll_list = filter_result_field(
            result_list=filter_result_field(
                result_list=enroll_list,
                alias_dict=forward_filed_map
            ),
            remove_filed_list=["field_1", "field_2", "field_3", "field_4", "field_5", "field_6", "field_7", "field_8", "field_9", "field_10"]
        )
        # 拼接报名用户信息
        user_info_map = {i["user_id"]: i for i in DetailInfoService.get_list_detail(None, user_id_list=[i["user_id"] for i in enroll_list])}
        for j in enroll_list:
            j["enroll_user_info"] = user_info_map.get(j["user_id"], {})
        # 拼接发起人用户信息
        user_info_map = {i["user_id"]: i for i in DetailInfoService.get_list_detail(None, user_id_list=[i["enroll_user_id"] for i in enroll_list])}
        for j in enroll_list:
            j["initiator_info"] = user_info_map.get(j["user_id"], {})
        # 拼接信息表
        thread_map, err = ThreadListService.search([i["thread_id"] for i in enroll_list], True)
        for j in enroll_list:
            j["enroll_info"] = thread_map.get(j["thread_id"], {})
        # 返回数据
        return {'total': count, "page": page, "size": size, 'list': enroll_list}, None

    @staticmethod
    def record_edit(params, pk):
        pk, is_pass = force_transform_type(variable=params.pop("id", None) or pk, var_type="int")
        if not pk:
            return None, "非法请求，pk不能为空"

        # 扩展字段映射获取
        filed_map_list = list(EnrollRecordExtendField.objects.all().values("field", 'field_index'))
        reversal_filed_map = {
            item['field']: item['field_index'] for item in filed_map_list if item['field_index'] in EnrollRecordServices.enroll_record_extend_fields
        }

        # 修改内容检查处理
        try:
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                alias_dict=reversal_filed_map,
                is_remove_empty=True,
                filter_filed_list=list(reversal_filed_map.keys()) + [
                    "enroll_id|int",
                    "apply_subitem_ids|list_int",
                    "user_id|int",
                    "enroll_auth_status|int",
                    "enroll_pay_status|int",
                    "enroll_status_code|int",
                    "create_time|date",
                    "price|float",
                    "deposit|float",
                    "count|int",
                    "main_amount|float",
                    "coupon_amount|float",
                    "again_reduction|float",
                    "subitems_amount|float",
                    "deposit_amount|float",
                    "amount|float",
                    "paid_amount|float",
                    "unpaid_amount|float",
                    "fee|float",
                    "photos|json",
                    "files|json",
                    "score|float",
                    "reply",
                    "remark",
                    "finish_time|date",
                    "again_price|float",
                    "again_fee|float",
                    "initiator_again_price|float",
                    "estimated_time|date",
                    "update_time|date",
                ],
            )
        except ValueError as e:
            return None, str(e)

        # 数据验证
        record_obj = EnrollRecord.objects.filter(id=pk)
        if not record_obj.first():
            return None, "没有找到id为" + str(pk) + "的记录"

        # 数据进行需改
        try:
            record_obj.update(**params)
        except Exception as e:
            return None, "修改异常:" + str(e)
        return None, None

    @staticmethod
    def record_del(pk, search_params=None):
        if pk:
            record_obj = EnrollRecord.objects.filter(id=pk)
        elif search_params and isinstance(search_params, dict):
            record_obj = EnrollRecord.objects.filter(**search_params)
        else:
            return None, "找不到要删除的数据"

        if not record_obj:
            return None, None
        try:
            record_obj.delete()
        except Exception as e:
            return None, "删除异常:" + str(e)
        return None, None

    @staticmethod
    def record_detail(pk: int = None, search_params: dict = None, filter_fields: "str|list" = None):
        """
        报名记录详情
        :param filter_fields: 过滤字段
        :param pk: 查询主键
        :param search_params: 添加搜索，但是仅仅返回第一条
        :return: date, err
        """
        search_params, is_pass = force_transform_type(variable=search_params, var_type="dict", default={})
        # 扩展字段映射获取
        filed_map_list = list(EnrollRecordExtendField.objects.all().values("field", 'field_index'))
        filed_map = {item['field_index']: item['field'] for item in filed_map_list}

        # =================== 构建ORM搜索数据 ==============================
        main_record_obj = EnrollRecord.objects.annotate(
            thread_id=F("enroll__thread_id")
        )
        if search_params:
            main_record_detail = main_record_obj.filter(**search_params).first()
        else:
            main_record_detail = main_record_obj.filter(id=pk).first()
        # 报名记录不存在，返回给用户提示
        if not main_record_detail:
            return None, "不存在该报名记录"
        main_record_detail = EnrollRecordListSerializer(main_record_detail).data
        # =================== 构建ORM搜索数据 ==============================

        # =================== 多表信息并拼接 start ==============================
        # 分项记录拼接
        main_record_detail["subitem_record_list"], err = EnrollSubitemRecordService.list({"enroll_record_id": pk}, False)
        # 信息表
        thread_id = main_record_detail.get("thread_id", None)
        if thread_id:
            thread_info, thread_err = ThreadItemService.detail(
                pk=thread_id,
                filter_fields=[
                    "id", "title", "subtitle", "content", "summary", "access_level", "author",
                    "ip", "has_enroll", "cover", "photos", "video", "files", "link",
                    "create_time", "update_time", "category_value", "category_name",
                    "category_platform_code",
                ]
            )
            if not thread_err and thread_info:
                main_record_detail["thread_info"] = thread_info
        # 获取用户表
        user_id = main_record_detail["user_id"]
        if user_id:
            user_info_list = DetailInfoService.get_list_detail(
                user_id_list=[main_record_detail["user_id"]],
                filter_fields=['real_name', 'avatar', 'user_name', 'full_name', 'nickname', 'phone']
            )  # 拼接用户信息
            if not err and user_info_list and isinstance(user_info_list, list):
                main_record_detail.update(user_info_list[0])
        # =================== 多表信息并拼接 end   ==============================

        # ====================== 扩展字段过滤  start ==================================
        # 扩展字段过滤 不涉及ORM。所以字段不强制验证，仅仅使用 default_field_list限制即可。
        # 拼接的字段，需要而额外开放白名单
        split_joint_fields = ["subitem_record_list", "thread_info", 'real_name', 'avatar', 'user_name', 'full_name', 'nickname', 'phone']
        filter_filed_list = filter_fields_handler(
            input_field_expression=filter_fields,
            default_field_list=EnrollRecordServices.enroll_record_fields + split_joint_fields
        )
        # 经过两次的替换过滤移除得到目标结果
        main_record_detail = format_params_handle(
            param_dict=format_params_handle(
                param_dict=main_record_detail,
                filter_filed_list=filter_filed_list,  # 过滤字段
                alias_dict=filed_map  # 替换扩展字段
            ),
            remove_filed_list=EnrollRecordServices.enroll_record_extend_fields,  # 移除扩展字段
            alias_dict={"enroll": "enroll_id"}
        )
        # ====================== 扩展字段过滤  end  ==================================
        return main_record_detail, None

    @staticmethod
    def appoint(enroll_id: int = None, record_id: int = None, subitem_id: int = None, **kwargs):
        """
        指派报名记录于报名分项关系，生成一条报名分项记录。
        :param enroll_id: 报名ID
        :param record_id: 记录ID
        :param subitem_id: 分项ID
        :return: None，err_msg
        """
        # 参数校验
        if enroll_id is None or record_id is None or subitem_id is None:
            return None, "参数错误"

        # 状态码常量
        draft_code, is_pass = force_transform_type(variable=kwargs.get("draft_code", 124), var_type="int", default=124)  # 草稿code
        enrolled_code, is_pass = force_transform_type(variable=kwargs.get("enrolled_code", 356), var_type="int", default=356)  # 已报名code
        enrolling_code, is_pass = force_transform_type(variable=kwargs.get("enrolling_code", 234), var_type="int", default=234)  # 报名中code

        try:
            # 获取报名主体，确认传的enroll_id是否存在
            enroll_query_set = Enroll.objects.filter(id=enroll_id, enroll_status_code__regex=enrolling_code).first()
            if not enroll_query_set:
                return None, "没有找到可以报名的报名主体"

            # 报名记录检查是否存在
            this_record_obj = EnrollRecord.objects.filter(id=record_id).exclude(enroll_status_code=draft_code).first()
            if not this_record_obj:
                return None, "找不到该报名人记录"
            this_record_json = this_record_obj.to_json()

            # 检查是否和报名者的预期相符合
            apply_subitem_ids = this_record_json.get("apply_subitem_ids", None)
            if apply_subitem_ids and isinstance(apply_subitem_ids, list) and not subitem_id in apply_subitem_ids:
                return None, "和报名者的预期并不相符，无法指派该该分类，请支配报名者预期的分项"

            # 校验报名分项是否存在
            enroll_subitem_obj = EnrollSubitem.objects.filter(id=subitem_id).first()
            if not enroll_subitem_obj:
                return None, "subitem_id错误，找不到可以指派的任务"

            # 判断当前的任务是否已经被指派过
            enroll_subitem_record_obj = EnrollSubitemRecord.objects.filter(enroll_subitem_id=subitem_id) \
                .exclude(enroll_subitem_status_code=draft_code).first()
            if not enroll_subitem_record_obj is None:
                return None, "该任务已经指派过了，无法在指派给其他人。"

            # 判断是否剩余可指派的任务
            need_count = enroll_query_set.count or 0  # 需求份数
            enrolled_count = EnrollSubitemRecord.objects.annotate(enroll_id=F("enroll_record__enroll_id")) \
                .filter(enroll_id=enroll_id).exclude(enroll_subitem_status_code=draft_code).values("id").count()
            if enrolled_count >= int(need_count):  # 报名成功的数量
                return None, "已经没有剩余的任务了，无法再次指派"

            # 指派某个人做哪一个任，生成任务记录（生成一条报名分项记录）
            insert_params = {
                "enroll_record_id": record_id,
                "enroll_subitem_id": subitem_id,
                "user_id": this_record_obj.user_id,
                "enroll_subitem_status_code": enrolled_code,
                "price": enroll_subitem_obj.price,
                "count": enroll_subitem_obj.count,
                "subitem_amount": enroll_subitem_obj.price
            }
            EnrollSubitemRecord.objects.create(**insert_params)

            # 判断是否多个任务指派给一个人，修改报名记录得到count, count表示这个报名人拥有几个任务（分项记录） 修改当前的报名记录未被指派状态，变成已经指派
            subitem_record_count = EnrollSubitemRecord.objects.filter(enroll_record_id=record_id).count()
            subitems_amount = (this_record_obj.price or 0 + this_record_obj.again_price or 0) * subitem_record_count
            # 更新当前的报名记录和指派的分项
            EnrollRecord.objects.filter(id=record_id).update(enroll_status_code=enrolled_code, count=subitem_record_count, amount=subitems_amount)
            EnrollSubitem.objects.filter(enroll_id=enroll_id).update(enroll_subitem_status_code=enrolled_code)

            # 再次查询 报名成功的数量, 判断是否可以进入补差补差价。
            # 查询当前指派的人数，和需求的数量，如果相同则指派满，<报名中> ==>> <已报名>
            again_enrolled_count = EnrollSubitemRecord.objects.annotate(enroll_id=F("enroll_record__enroll_id")).filter(
                enroll_id=enroll_id,
                enroll_subitem_status_code=enrolled_code
            ).values("id").count()
            if again_enrolled_count >= need_count:
                # 把剩余没有指派的人全部变成草稿状态
                EnrollRecord.objects.filter(enroll_id=enroll_id).exclude(enroll_status_code=enrolled_code).update(enroll_status_code=draft_code)
                # 如果是一人被指派多份的时候就会出现问题，所以应该使用左连接，以报名分项记录为主表连接报名记录表，enroll_id为搜索
                valuate_result, err = ValuationService.valuation_detailed_list(enroll_id)
                write_to_log(level="info", prefix="指派计价结果：", content="enroll_id:" + str(enroll_id) + "valuate_result:" + str(valuate_result or ""))
                if err:
                    write_to_log(level="error", prefix="报名指派重新计价异常：", content=err)
                    return None, err
                # 报名主表更新
                Enroll.objects.filter(id=enroll_id).update(
                    enroll_status_code=enrolled_code,
                    unpaid_amount=valuate_result["unpaid_amount"],
                    amount=valuate_result["amount"],
                    commision=valuate_result["commision"],
                    subitems_amount=valuate_result["subitems_amount"],
                )
            return None, None

        except Exception as e:
            write_to_log(level="error", prefix="报名指派异常", err_obj=e)
            return None, str(e)

    @staticmethod
    def re_appoint(
            enroll_id: int = None,
            subitem_id: int = None,
            old_record_id: int = None,
            new_record_id: int = None,
            **kwargs
    ):
        """
        重新指派，已报名报名记录和报名分项记录变成草稿，
        :param subitem_id: 原来的分项ID
        :param old_record_id: 原指派的报名记录
        :param new_record_id: 重新指派的报名记录
        :param enroll_id: 报名ID
        :return: None，err_msg
        """
        # 参数校验
        enroll_id, is_pass = force_transform_type(variable=enroll_id, var_type="int")
        old_record_id, is_pass = force_transform_type(variable=old_record_id, var_type="int")
        subitem_id, is_pass = force_transform_type(variable=subitem_id, var_type="int")
        new_record_id, is_pass = force_transform_type(variable=new_record_id, var_type="int")
        if enroll_id is None or old_record_id is None or new_record_id is None or subitem_id is None:
            return None, "参数错误"
        # 状态码常量
        draft_code, is_pass = force_transform_type(variable=kwargs.get("draft_code", 124), var_type="int", default=124)  # 草稿code
        enrolled_code, is_pass = force_transform_type(variable=kwargs.get("enrolled_code", 356), var_type="int", default=356)  # 已报名code
        enrolling_code, is_pass = force_transform_type(variable=kwargs.get("enrolling_code", 234), var_type="int", default=234)  # 报名中code
        try:
            # ================= section 边界验证 start =============================
            # 获取报名主体，确认传的enroll_id是否存在
            enroll_query_set = Enroll.objects.filter(id=enroll_id, enroll_status_code__in=[enrolling_code, enrolled_code]).first()
            if not enroll_query_set:
                return None, "没有找到可以报名的报名主体"

            # 判断当前状态是否在报名中或者已报名
            enroll_dict = enroll_query_set.to_json()
            current_enroll_status_code = enroll_dict.get("enroll_status_code", None)
            if not current_enroll_status_code in [enrolling_code, enrolled_code]:
                return None, "当前的状态不可以重新指派"

            # 报名记录检查是否存在
            old_record = EnrollRecord.objects.filter(id=old_record_id).exclude(enroll_status_code=draft_code).first()
            new_record = EnrollRecord.objects.filter(id=old_record_id).first()
            if not old_record or not new_record:
                return None, "不是有效的报名记录ID"

            # 校验报名分项是否存在
            old_enroll_subitem_obj = EnrollSubitem.objects.filter(id=subitem_id, enroll_id=enroll_id).first()
            if not old_enroll_subitem_obj:
                return None, "subitem_id错误，找不到可以指派的任务"
            # ================= section 边界验证 start =============================

            # ================= section 边界验证通过，进行重新指派 start =============================
            # note 已报名未选中的状态码为草稿，报名中未选中的报名记录状态码是报名中（多份会走该逻辑）
            update_code = draft_code if current_enroll_status_code == enrolled_code else current_enroll_status_code
            # 修改报名记录
            EnrollRecord.objects.filter(id=old_record_id).update(enroll_status_code=update_code)
            EnrollRecord.objects.filter(id=new_record_id).update(enroll_status_code=enrolled_code)
            # 报名分项记录修改
            EnrollSubitemRecord.objects.filter(
                enroll_subitem_id=subitem_id,
                enroll_record_id=old_record_id
            ).update(enroll_record_id=new_record_id)
            # ================= section 边界验证通过，进行重新指派 end   =============================
            return None, None

        except Exception as e:
            write_to_log(level="error", prefix="报名指派异常", err_obj=e)
            return None, str(e)

    @staticmethod
    def old_appoint(enroll_id, record_id, subitem_id):
        """
        镖行天下，报名人指派。(在接入流程控制的老版本指派接口) TODO 后面将一处old接口
        :param enroll_id: 报名ID
        :param record_id: 记录ID
        :param subitem_id: 分项ID
        :return: None，err_msg
        """
        # 定义常量
        appointed_code = 356  # 报名记录被指派的状态码，PS：当前认为356是报名的状态码，报名完成状态
        appointed_start = "^3"
        make_up_difference_code = 243  # 补差价状态码
        make_up_difference_start = "^2"
        rough_draft_code = 124  # 草稿状态码
        rough_draft_start = "^1"
        try:
            # 获取报名主体，确认传的enroll_id是否存在
            enroll_query_set = Enroll.objects.filter(id=enroll_id, enroll_status_code__regex=make_up_difference_start).first()
            if not enroll_query_set:
                return None, "没有找到报名主体"

            # 报名记录检查是否存在
            this_record_obj = EnrollRecord.objects.filter(id=record_id).first()
            if not this_record_obj:
                return None, "找不到该报名人记录"

            # 判断这个报名用户是否被重复指派，暂不限制
            # if this_record_obj.enroll_status_code == appointed_code:
            #     return None, "当前报名人已经指派过了，请勿重复指派"

            # 校验报名分项是否存在
            enroll_subitem_obj = EnrollSubitem.objects.filter(id=subitem_id).first()
            if not enroll_subitem_obj:
                return None, "subitem_id错误，找不到可以指派的任务"

            # 判断是否剩余可指派的任务
            need_count = enroll_query_set.count or 0  # 需求份数
            enrolled_count = EnrollSubitemRecord.objects.annotate(enroll_id=F("enroll_record__enroll_id")) \
                .filter(
                enroll_id=enroll_id,
                enroll_subitem_status_code__regex=appointed_start
            ).values("id").count()  # 报名成功的数量
            if enrolled_count >= int(need_count):
                return None, "已经没有剩余的任务了，无法再次指派"

            # 判断当前的任务是否已经被指派过
            enroll_subitem_record_obj = EnrollSubitemRecord.objects.filter(enroll_subitem_id=subitem_id).exclude(enroll_subitem_status_code__regex=rough_draft_start).first()
            if not enroll_subitem_record_obj is None:
                return None, "该任务已经指派过了，无法在指派给其他人。"

            # 修改当前的报名记录为被指派状态
            EnrollRecord.objects.filter(id=record_id).update(enroll_status_code=appointed_code)

            # 指派某个人做哪一个任，生成任务记录（生成一条报名分项记录）
            insert_params = {
                "enroll_record_id": record_id,
                "enroll_subitem_id": subitem_id,
                "user_id": this_record_obj.user_id,
                "enroll_subitem_status_code": appointed_code,
                "price": enroll_subitem_obj.price,
                "count": enroll_subitem_obj.count,
                "subitem_amount": enroll_subitem_obj.price
            }
            EnrollSubitemRecord.objects.create(**insert_params)

            # 判断是否多个任务指派给一个人，修改报名记录得到count, count表示这个报名人拥有几个任务（分项记录）
            subitem_record_count = EnrollSubitemRecord.objects.filter(enroll_record_id=record_id).count()
            subitems_amount = (this_record_obj.price or 0 + this_record_obj.initiator_again_price or 0) * subitem_record_count
            EnrollRecord.objects.filter(id=record_id).update(count=subitem_record_count, amount=subitems_amount)

            # 再次查询 报名成功的数量, 判断是否可以进入补差补差价。
            again_enrolled_count = EnrollSubitemRecord.objects.annotate(enroll_id=F("enroll_record__enroll_id")) \
                .filter(
                enroll_id=enroll_id,
                enroll_subitem_status_code__regex=appointed_start
            ).values("id").count()

            # 查询当前指派的人数，和需求的数量，如果相同则指派满，则进入下一阶段（代补差价）
            if again_enrolled_count >= need_count:
                # 把剩余没有指派的人全部变成草稿状态
                EnrollRecord.objects.filter(enroll_id=enroll_id).exclude(enroll_status_code__regex=appointed_code).update(enroll_status_code=rough_draft_code)
                # 如果是一人被指派多份的时候就会出现问题，所以应该使用左连接，以报名分项记录为主表连接报名记录表，enroll_id为搜索
                valuate_result, err = ValuationService.valuation_detailed_list(enroll_id)
                write_to_log(level="info", prefix="指派计价结果：", content="enroll_id:" + str(enroll_id) + "valuate_result:" + str(valuate_result or ""))
                if err:
                    write_to_log(level="error", prefix="报名指派重新计价异常：", content=err)

                # 报名主表更新
                Enroll.objects.filter(id=enroll_id).update(
                    unpaid_amount=valuate_result["unpaid_amount"],
                    amount=valuate_result["amount"],
                    commision=valuate_result["commision"],
                    subitems_amount=valuate_result["subitems_amount"],
                )
                # 修改全部的
                EnrollStatusCodeService.batch_edit_code(enroll_id=enroll_id, code=make_up_difference_code)
            return None, None

        except Exception as e:
            write_to_log(level="error", prefix="报名指派异常", err_obj=e)
            return None, str(e)

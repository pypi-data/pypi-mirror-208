# encoding: utf-8
"""
@project: djangoModel->enroll_statistics
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 报名统计服务
@created_time: 2023/2/22 14:31
"""
import datetime

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDay, Round

from xj_user.services.user_relate_service import UserRelateToUserService
from xj_user.services.user_service import UserService
from ..models import Enroll, EnrollRecord, EnrollSubitemRecord
from ..utils.custom_tool import format_params_handle
from ..utils.join_list import JoinList


class EnrollStatisticsServices(object):
    """报名主项统计服务(发布人统计)"""

    @staticmethod
    def every_one_total(params=None, need_Pagination=True):
        """
        每个人汇总统计报名表（后台展示），可以根据事件和状态码筛选。
        :param params:
        :return: [{
        "user_id":用户ID,
        "user_name": 用户名称,
        "nick_name": 用户名称,
        "count":"发布次数",
        "amount_total":"总收合计"，
        "paid_amount_total":"为首合计",
        "paid_amount_total":"以收合计",
        "average_price":"平均价格",
        "commision_total":"总佣金",
        "counts_total":"份数总计"
        }]，err_msg
        """
        if params is None:
            params = {}
        page = params.get("page", 1)
        size = params.get("size", 10)
        # 字段过滤
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                # ID 编码 code 等等筛选
                "enroll_id", "thread_id", "category_id", "user_id", "enroll_rule_group_id", "trading_relate", "region_code",
                "occupy_room", "enroll_status_code", "user_relate_type_id",
                # 布尔条件筛选
                "need_vouch", "need_deposit", "need_imprest", "enable_pool", "hide_price", "hide_user", "has_repeat",
                "has_subitem", "has_audit",
                # 时间区间筛选 注意：所有的数值区间参数开始start后缀开始，以end结尾。
                "open_time", "close_time", "launch_time", "finish_time", "spend_time", "create_time", "update_time",
                "open_time_start", "close_time_start", "launch_time_start", "finish_time_start", "spend_time_start", "create_time_start", "update_time_start",
                "open_time_end", "close_time_end", "launch_time_end", "finish_time_end", "spend_time_end", "create_time_end", "update_time_end",
                # 数值区间筛选，注意：所有的数值区间参数开始min后缀开始，以max结尾。
                "min_number", "max_number", "max_count_apiece", "min_count_apiece",  # 不做区间处理
                "price", "count", "fee", "subitems_amount", "amount", "paid_amount", "unpaid_amount", "commision", "reduction", "pool_limit", "pool_stopwatch", "deposit",
                "price_min", "count_min", "fee_min", "subitems_amount_min", "amount_min", "paid_amount_min", "unpaid_amount_min", "commision_min", "reduction_min", "pool_limit_min",
                "pool_stopwatch_min", "deposit_min",
                "price_max", "count_max", "fee_max", "subitems_amount_max", "amount_max", "paid_amount_max", "unpaid_amount_max", "commision_max", "reduction_max", "pool_limit_max",
                "pool_stopwatch_max", "deposit_max",
            ],
            remove_filed_list=None,
            alias_dict={
                "enroll_id": "id",
                # 时间区间还原成orm表达式
                "open_time_start": "open_time__gte", "close_time_start": "close_time__gte", "launch_time_start": "launch_time__gte", "finish_time_start": "finish_time__gte",
                "spend_time_start": "spend_time__gte", "create_time_start": "create_time__gte", "update_time_start": "update_time__gte", "open_time_end": "open_time__lte",
                "close_time_end": "close_time__lte", "launch_time_end": "launch_time__lte", "finish_time_end": "finish_time__lte", "spend_time_end": "spend_time__lte",
                "create_time_end": "create_time__lte", "update_time_end": "update_time__lte",
                # 数值区间还原成orm表达式
                "price_min": "price__gte", "count_min": "count__gte", "fee_min": "fee__gte", "subitems_amount_min": "subitems_amount__gte", "amount_min": "amount__gte",
                "paid_amount_min": "paid_amount__gte", "unpaid_amount_min": "unpaid_amount__gte", "commision_min": "commision__gte", "reduction_min": "reduction__gte",
                "pool_limit_min": "pool_limit__gte", "pool_stopwatch_min": "pool_stopwatch__gte", "deposit_min": "deposit__gte",
                "price_max": "price__lte", "count_max": "count__lte", "fee_max": "fee__lte", "subitems_amount_max": "subitems_amount__lte", "amount_max": "amount__lte",
                "paid_amount_max": "paid_amount__lte", "unpaid_amount_max": "unpaid_amount__lte", "commision_max": "commision__lte", "reduction_max": "reduction__lte",
                "pool_limit_max": "pool_limit__lte", "pool_stopwatch_max": "pool_stopwatch__lte", "deposit_max": "deposit__lte",
            },
            is_remove_null=True
        )

        # 基础条件筛选出大致范围
        search_obj = Enroll.objects.filter(**params)

        # 用户关系搜索， TODO 如果后期 with_user_id_list大于2500个mysql会报错。所以这里存在性能优化空间
        user_relate_type_id = params.get("user_relate_type_id", None)
        user_id = params.get("user_id", None)
        if user_relate_type_id and user_id:
            relate_user_list, err = UserRelateToUserService.list(params={"need_pagination": 0, "user_id": user_id, "user_relate_type_id": user_relate_type_id})
            with_user_id_list = [i["with_user_id"] for i in relate_user_list]
            search_obj.filter(user_id__in=with_user_id_list)

        # 进行group分组计算
        group_obj = search_obj.values("user_id").annotate(
            push_count=Count("id"),
            average_price=Round(Avg("price")),
            amount_total=Round(Sum("amount")),
            paid_amount_total=Round(Sum("paid_amount")),
            unpaid_amount_total=Round(Sum("unpaid_amount")),
            commision_total=Round(Sum("commision")),
            count_total=Round(Sum("count"))
        )
        group_obj = group_obj.values(
            "user_id", "push_count", "average_price", "amount_total", "paid_amount_total", "unpaid_amount_total", "commision_total", "count_total"
        )
        total = group_obj.count()

        if need_Pagination:
            # 进行分页查询
            paginator = Paginator(group_obj, size)
            try:
                enroll_obj = paginator.page(page)
            except EmptyPage:
                enroll_obj = paginator.page(paginator.num_pages)
            except Exception as e:
                return None, f'{str(e)}'
            group_obj = enroll_obj

        # 报名汇总
        enroll_total_list = list(group_obj)
        # 查询 用户信息
        user_ids = [i["user_id"] for i in enroll_total_list if i["user_id"]]
        user_info_list, err = UserService.user_search(user_id_list=user_ids, need_map=False, filter_fields=["id", "user_name", "nickname", "phone"])
        # 拼接 用户信息
        enroll_total_list = JoinList(enroll_total_list, user_info_list, "user_id", "user_id").join()

        return {"page": page, "size": size, "total": total, "list": enroll_total_list, } if need_Pagination else enroll_total_list, None

    @staticmethod
    def every_day_total(params=None, need_Pagination=True):
        """
        每个人汇总统计，可以根据事件和状态码筛选。
        :param params:
        :return: data，err_msg
        """

        if params is None:
            params = {}
        page = params.get("page", 1)
        size = params.get("size", 10)
        today = datetime.date.today()
        last_thirty_day = today - datetime.timedelta(days=30)

        # 默认仅仅差30天内的数据
        params.setdefault("create_time_start", last_thirty_day.strftime("%Y-%m-%d 00:00:00"))
        params.setdefault("create_time_end", today.strftime("%Y-%m-%d 23:59:59"))
        create_time_start = params.get("create_time_start", None)
        create_time_end = params.get("create_time_end", None)

        # 字段过滤
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                # ID 编码 code 等等筛选
                "enroll_id", "thread_id", "category_id", "user_id", "enroll_rule_group_id", "trading_relate", "region_code",
                "occupy_room", "enroll_status_code", "user_relate_type_id",
                # 布尔条件筛选
                "need_vouch", "need_deposit", "need_imprest", "enable_pool", "hide_price", "hide_user", "has_repeat",
                "has_subitem", "has_audit",
                # 时间区间筛选 注意：所有的数值区间参数开始start后缀开始，以end结尾。
                "open_time", "close_time", "launch_time", "finish_time", "spend_time", "create_time", "update_time",
                "open_time_start", "close_time_start", "launch_time_start", "finish_time_start", "spend_time_start", "create_time_start", "update_time_start",
                "open_time_end", "close_time_end", "launch_time_end", "finish_time_end", "spend_time_end", "create_time_end", "update_time_end",
                # 数值区间筛选，注意：所有的数值区间参数开始min后缀开始，以max结尾。
                "min_number", "max_number", "max_count_apiece", "min_count_apiece",  # 不做区间处理
                "price", "count", "fee", "subitems_amount", "amount", "paid_amount", "unpaid_amount", "commision", "reduction", "pool_limit", "pool_stopwatch", "deposit",
                "price_min", "count_min", "fee_min", "subitems_amount_min", "amount_min", "paid_amount_min", "unpaid_amount_min", "commision_min", "reduction_min", "pool_limit_min",
                "pool_stopwatch_min", "deposit_min",
                "price_max", "count_max", "fee_max", "subitems_amount_max", "amount_max", "paid_amount_max", "unpaid_amount_max", "commision_max", "reduction_max", "pool_limit_max",
                "pool_stopwatch_max", "deposit_max",
            ],
            remove_filed_list=None,
            alias_dict={
                "enroll_id": "id",
                # 时间区间还原成orm表达式
                "open_time_start": "open_time__gte", "close_time_start": "close_time__gte", "launch_time_start": "launch_time__gte", "finish_time_start": "finish_time__gte",
                "spend_time_start": "spend_time__gte", "create_time_start": "create_time__gte", "update_time_start": "update_time__gte", "open_time_end": "open_time__lte",
                "close_time_end": "close_time__lte", "launch_time_end": "launch_time__lte", "finish_time_end": "finish_time__lte", "spend_time_end": "spend_time__lte",
                "create_time_end": "create_time__lte", "update_time_end": "update_time__lte",
                # 数值区间还原成orm表达式
                "price_min": "price__gte", "count_min": "count__gte", "fee_min": "fee__gte", "subitems_amount_min": "subitems_amount__gte", "amount_min": "amount__gte",
                "paid_amount_min": "paid_amount__gte", "unpaid_amount_min": "unpaid_amount__gte", "commision_min": "commision__gte", "reduction_min": "reduction__gte",
                "pool_limit_min": "pool_limit__gte", "pool_stopwatch_min": "pool_stopwatch__gte", "deposit_min": "deposit__gte",
                "price_max": "price__lte", "count_max": "count__lte", "fee_max": "fee__lte", "subitems_amount_max": "subitems_amount__lte", "amount_max": "amount__lte",
                "paid_amount_max": "paid_amount__lte", "unpaid_amount_max": "unpaid_amount__lte", "commision_max": "commision__lte", "reduction_max": "reduction__lte",
                "pool_limit_max": "pool_limit__lte", "pool_stopwatch_max": "pool_stopwatch__lte", "deposit_max": "deposit__lte",
            },
            is_remove_null=True
        )

        # 基础条件筛选出大致范围
        search_obj = Enroll.objects.filter(**params)

        # 用户关系搜索， TODO 如果后期 with_user_id_list大于2500个mysql会报错。所以这里存在性能优化空间
        user_relate_type_id = params.get("user_relate_type_id", None)
        user_id = params.get("user_id", None)
        if user_relate_type_id and user_id:
            relate_user_list, err = UserRelateToUserService.list(params={"need_pagination": 0, "user_id": user_id, "user_relate_type_id": user_relate_type_id})
            with_user_id_list = [i["with_user_id"] for i in relate_user_list]
            search_obj = search_obj.filter(user_id__in=with_user_id_list)

        # 进行group分组计算
        group_obj = search_obj.annotate(create_date=TruncDay("create_time")).values("create_date").annotate(
            push_count=Count("id"),
            average_price=Round(Avg("price")),
            amount_total=Round(Sum("amount")),
            paid_amount_total=Round(Sum("paid_amount")),
            unpaid_amount_total=Round(Sum("unpaid_amount")),
            commision_total=Round(Sum("commision")),
            count_total=Round(Sum("count"))
        ).order_by("-create_date")
        group_obj = group_obj.values(
            "create_date", "push_count", "amount_total", "average_price", "paid_amount_total", "unpaid_amount_total", "commision_total", "count_total"
        )
        total = group_obj.count()

        if need_Pagination:
            # 进行分页查询
            paginator = Paginator(group_obj, size)
            try:
                enroll_obj = paginator.page(page)
            except EmptyPage:
                enroll_obj = paginator.page(paginator.num_pages)
            except Exception as e:
                return None, f'{str(e)}'
            group_obj = enroll_obj

        # 报名汇总
        enroll_total_list = list(group_obj)
        return {
                   "page": page,
                   "size": size,
                   "total": total,
                   "create_time_start": create_time_start,
                   "create_time_end": create_time_end,
                   "list": enroll_total_list,
               } if need_Pagination else enroll_total_list, None

    @staticmethod
    def statistics_by_day():
        """
        小程序临时接口
        :return:
        """
        this_day = str(datetime.date.today())
        this_day_start = this_day + " 00:00:00"
        this_day_end = this_day + " 23:59:59"
        before_seven_day_start = ((datetime.datetime.now()) + datetime.timedelta(days=-7)).strftime("%Y-%m-%d") + " 00:00:00"
        result = {}
        # 今日成交数量
        # this_day_obj_count = Enroll.objects.filter(Q(enroll_status_code=680) | Q(enroll_status_code=80)).filter(create_time__gt=this_day_start, create_time__lt=this_day_end).count()
        this_day_obj_count = Enroll.objects.filter(create_time__gt=this_day_start, create_time__lt=this_day_end).count()
        result["this_day_count"] = this_day_obj_count
        # 近七日的成交数量与金额
        # nearly_seven_days = list(
        #     Enroll.objects.filter(Q(enroll_status_code=680) | Q(enroll_status_code=80))
        #         .filter(create_time__gt=before_seven_day_start, create_time__lt=this_day_end) \
        #         .annotate(created_day=TruncDay("create_time")) \
        #         .values("created_day") \
        #         .annotate(deel_count=Count("id"))
        #         .annotate(deel_amount=Sum("amount"))
        #         .values("created_day", "deel_count", "deel_amount")
        # )

        nearly_seven_days = list(
            Enroll.objects.filter(create_time__gt=before_seven_day_start, create_time__lt=this_day_end) \
                .annotate(created_day=TruncDay("create_time")) \
                .values("created_day") \
                .annotate(deel_count=Count("id"))
                .annotate(deel_amount=Sum("amount"))
                .values("created_day", "deel_count", "deel_amount")
        )
        day_map = {}
        for i in nearly_seven_days:
            i["created_day"] = i["created_day"].strftime('%Y-%m-%d')
            i["deel_amount"] = round(float(i["deel_amount"]), 2) if i["deel_amount"] else 0
            day_map[i["created_day"]] = i
        nearly_seven_days_list = []
        for i in range(7):
            this_day = ((datetime.datetime.now()) + datetime.timedelta(days=-i)).strftime("%Y-%m-%d")
            nearly_seven_days_list.append(day_map.get(this_day) if day_map.get(this_day) else {"created_day": this_day, "deel_amount": 0, "deel_count": 0})
        result["nearly_seven_days"] = nearly_seven_days_list

        # 总成交金额和总的成交数量
        # total_deel_amount = Enroll.objects.filter(Q(enroll_status_code=680) | Q(enroll_status_code=80)).aggregate(total_deel_amount=Sum('amount'))
        # total_deel_count = Enroll.objects.filter(Q(enroll_status_code=680) | Q(enroll_status_code=80)).aggregate(total_deel_count=Count('id'))

        total_deel_amount = Enroll.objects.filter().aggregate(total_deel_amount=Sum('amount'))
        total_deel_count = Enroll.objects.filter().aggregate(total_deel_count=Count('id'))

        result["total_deel_amount"] = total_deel_amount["total_deel_amount"] if total_deel_amount["total_deel_amount"] else 0
        result["total_deel_count"] = total_deel_count["total_deel_count"] if total_deel_count["total_deel_count"] else 0

        # 代发佣金和提成
        await_commission_main = EnrollRecord.objects.exclude(Q(enroll_status_code=680) | Q(enroll_status_code=80)).aggregate(total_deel_amount=Sum('amount'))
        await_commission_subitem = EnrollSubitemRecord.objects.exclude(Q(enroll_subitem_status_code=680) | Q(enroll_subitem_status_code=80)).aggregate(total_subitem_amount=Sum('subitem_amount'))

        already_commission_main = EnrollRecord.objects.filter(Q(enroll_status_code=680) | Q(enroll_status_code=80)).aggregate(total_deel_amount=Sum('amount'))
        already_commission_subitem = EnrollSubitemRecord.objects.filter(Q(enroll_subitem_status_code=680) | Q(enroll_subitem_status_code=80)).aggregate(total_subitem_amount=Sum('subitem_amount'))
        result["await_commission_main"] = round(await_commission_main["total_deel_amount"], 2) if await_commission_main["total_deel_amount"] else 0
        result["await_commission_subitem"] = round(await_commission_subitem["total_subitem_amount"], 2) if await_commission_subitem["total_subitem_amount"] else 0
        result["already_commission_main"] = round(already_commission_main["total_deel_amount"], 2) if already_commission_main["total_deel_amount"] else 0
        result["already_commission_subitem"] = round(already_commission_subitem["total_subitem_amount"], 2) if already_commission_subitem["total_subitem_amount"] else 0

        return result, None

    @staticmethod
    def statistics_by_user(user_id=None):
        """
        小程序临时统计接口
        :param user_id:
        :return:
        """
        if not user_id:
            return None, "user_id 不能为空"
        this_day = str(datetime.date.today())
        this_day_start = this_day + " 00:00:00"
        this_day_end = this_day + " 23:59:59"
        today_order_num = Enroll.objects.filter(user_id=user_id).filter(create_time__gt=this_day_start, create_time__lt=this_day_end).count()
        # .filter(Q(enroll_status_code=680) | Q(enroll_status_code=80)) \

        today__undertake_num = EnrollRecord.objects.filter(user_id=user_id) \
            .filter(create_time__gt=this_day_start, create_time__lt=this_day_end, ) \
            .exclude(enroll_status_code=124).count()
        # .filter(Q(enroll_status_code=680) | Q(enroll_status_code=80))
        total_order_num = Enroll.objects.filter(user_id=user_id).count()
        total__undertake_num = EnrollRecord.objects.filter(user_id=user_id).exclude(enroll_status_code=124).count()

        return {"today_order_num": today_order_num, "today__undertake_num": today__undertake_num, "total_order_num": total_order_num, "total__undertake_num": total__undertake_num}, None

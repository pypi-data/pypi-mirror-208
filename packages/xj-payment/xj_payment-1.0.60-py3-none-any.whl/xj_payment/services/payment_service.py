import logging
import random
import sys
from datetime import datetime

import pytz
import requests
import time
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.core.paginator import Paginator
from django.db.models import F
from django.forms import model_to_dict
from django.utils import timezone
from pathlib import Path
from main.settings import BASE_DIR
from xj_enroll.service.enroll_services import EnrollServices
from xj_payment.utils.join_list import JoinList
from xj_thread.services.thread_list_service import ThreadListService
from xj_user.models import Platform
from xj_user.services.user_platform_service import UserPlatformService
from xj_user.services.user_sso_serve_service import UserSsoServeService
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict
from ..utils.custom_tool import format_list_handle, format_params_handle, write_to_log
from ..models import PaymentPayment, PaymentStatus
from ..services.payment_wechat_service import PaymentWechatService

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))

# 小程序appid
sub_appid = main_config_dict.wechat_merchant_app_id or module_config_dict.wechat_merchant_app_id or ""
# 服务号appid
subscription_app_id = main_config_dict.wechat_subscription_app_id or module_config_dict.wechat_subscription_app_id or ""
# 商户名称
merchant_name = main_config_dict.merchant_name or module_config_dict.merchant_name or ""


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


class PaymentService:
    @staticmethod
    def get(params):
        limit = params.pop('limit', 20)
        page = params.pop('page', 20)
        list_obj = PaymentPayment.objects.filter(**params).order_by('-id')
        if params.get("create_time_start", None) and params.get("create_time_end", None):
            list_obj = list_obj.filter(
                create_time__range=(params['create_time_start'], params['create_time_end']))

        list_obj = list_obj.annotate(payment_status=F("payment_status__payment_status"),
                                     payment_code=F("payment_status__payment_code"))

        if params.get("payment_status", None):
            list_obj = list_obj.filter(payment_status__payment_status=params.get("payment_status", None), )

        list_obj = list_obj.extra(select={
            'user_full_name': 'SELECT full_name FROM user_base_info WHERE user_base_info.id = payment_payment.user_id'}
        )
        list_obj = list_obj.extra(select={
            'title': 'SELECT thread.title FROM enroll_enroll left join  thread on enroll_enroll.thread_id=thread.id WHERE enroll_enroll.id = payment_payment.enroll_id'}
        )
        count = list_obj.count()
        list_obj = list_obj.values(
            "id",
            "transact_no",
            "order_no",
            "transact_id",
            "enroll_id",
            "order_id",
            "user_id",
            "subject",
            "total_amount",
            "buyer_pay_amount",
            "point_amount",
            "invoice_amount",
            "price_off_amount",
            "pay_mode",
            "order_status_id",
            "payment_status_id",
            "nonce_str",
            "order_time",
            "create_time",
            "modify_time",
            "payment_time",
            "refunt_time",
            "close_time",
            "voucher_detail",
            "snapshot",
            "more",
            "user_full_name",
            "title",
            "payment_status"

        ).annotate(payment_status=F('payment_status__payment_status'), )
        res_set = Paginator(list_obj, limit).get_page(page)
        page_list = []
        if res_set:
            page_list = list(res_set.object_list)
        for v in page_list:
            v['total_amount'] = float(v['total_amount']) / 100 if v['total_amount'] is not None else 0
            v['point_amount'] = float(v['point_amount']) / 100 if v['point_amount'] is not None else 0
            v['buyer_pay_amount'] = float(v['buyer_pay_amount']) / 100 if v['buyer_pay_amount'] is not None else 0
            v['invoice_amount'] = float(v['invoice_amount']) / 100 if v['invoice_amount'] is not None else 0
            v['price_off_amount'] = float(v['price_off_amount']) / 100 if v['price_off_amount'] is not None else 0

        return {'count': count, 'page': page, 'limit': limit, "list": page_list}, None

    @staticmethod
    def list(params, filter_fields=None, need_pagination=True):
        size = params.pop('size', 10)
        page = params.pop('page', 1)
        if params.get("is_all", None):
            params.pop("is_all")
            params.pop("user_id")
        payment_obj = PaymentPayment.objects
        filter_fields_list = filter_fields.split(";") if filter_fields else []
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "id", "transact_no", "order_no", "transact_id", "enroll_id", "order_id",
                "user_id", "subject", "total_amount", "buyer_pay_amount", "point_amount",
                "invoice_amount", "price_off_amount", "pay_mode", "order_status_id", "create_time",
                "payment_status_id", "nonce_str", "order_time", "modify_time", "payment_time", "refunt_time",
                "close_time",
                "create_time_start", "create_time_end"
            ],
            split_list=["user_id_list", "id_list", "enroll_id_list", "thread_id_list"],
            alias_dict={
                "modify_time_start": "modify_time__gte", "modify_time_end": "modify_time__lte",
                "create_time_start": "create_time__gte", "create_time_end": "create_time__lte",
                "enroll_category_value": "category__value",
                "thread_id_list": "thread_id__in", "enroll_id_list": "enroll_id__in", "id_list": "id__in",
            },
        )
        payment_obj = payment_obj.filter(**params).order_by("-id").values(*filter_fields_list)

        # if not need_pagination:
        #     return list(payment_obj), None
        # 分页展示
        paginator = Paginator(payment_obj, size)
        try:
            payment_obj = paginator.page(page)
        except EmptyPage:
            payment_obj = paginator.page(paginator.num_pages)
        except Exception as e:
            return None, f'{str(e)}'

        data = list(payment_obj.object_list)
        if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
            from xj_enroll.service.enroll_services import EnrollServices

            enroll_id_list = [item.get("enroll_id", None) for item in data]
            enroll_list, err = EnrollServices.enroll_list({"id_list": enroll_id_list}, "thread_id")
            if enroll_list:
                data = JoinList(data, enroll_list['list'], "enroll_id", "id").join()

        thread_id_list = [item.get("thread_id", None) for item in data]
        thread_list, err = ThreadListService.search(thread_id_list, filter_fields="title")
        if thread_list:
            data = JoinList(data, thread_list, "thread_id", "id").join()

        data = PaymentService.format_dates(data,
                                           ['create_time', "order_time", "modify_time", "payment_time",
                                            "refunt_time",
                                            "close_time"])

        return {'total': paginator.count, "page": page, "size": size, 'list': data}, None

    # 退款总接口
    @staticmethod
    def refund(params):
        data = params
        data['transaction_id'] = params['transaction_id']  # 支付单号
        data['refund_fee'] = float(params['refund_amount']) * 100  # 元转分
        data['out_trade_no'] = timezone.now().strftime('%Y%m%d%H%M%S') + ''.join(
            map(str, random.sample(range(0, 9), 4)))
        # 支付方式检查
        if params['payment_method'] == "WECHAT":  # 微信退款
            payment = PaymentWechatService.payment_refund(data)
        else:
            payment = "退款方式不存在"

        return payment

    # 支付总接口
    @staticmethod
    def pay(params):
        data = params
        # 验证支付方式
        payment_method = params.get("payment_method", None)
        # 大写转小写
        payment_method = payment_method.lower()
        payment_method_list = ["applets", "appletsv3", "balance", "wechat_web"]
        if not PaymentService.find(payment_method_list, payment_method):
            return None, "支付方式不存在"

        # 随机生成订单号
        out_trade_no = timezone.now().strftime('%Y%m%d%H%M%S') + ''.join(
            map(str, random.sample(range(0, 9), 4)))
        params['out_trade_no'] = out_trade_no

        # 判断是否是报名订单
        if params['enroll_id']:
            enroll_data, err_txt = EnrollServices.enroll_detail(params['enroll_id'])
            if err_txt:
                return None, "报名记录不存在"
            data['enroll_id'] = enroll_data['id']
            data['total_fee'] = float(enroll_data['unpaid_amount']) * 100  # 元转分

        # 返回datetime格式的时间
        tz = pytz.timezone('Asia/Shanghai')
        now_time = timezone.now().astimezone(tz=tz).strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')

        payment_status_set = PaymentStatus.objects.filter(payment_status="未支付").first()
        payment_data = {
            "order_no": out_trade_no,
            "enroll_id": data['enroll_id'],
            "user_id": data['user_id'],
            "total_amount": int(data['total_fee']),
            "create_time": now,
            "payment_status_id": payment_status_set.id
        }

        platform_set, err = UserPlatformService.payment_get_platform_info(params['platform_id'])
        if err:
            data['platform'] = merchant_name
        else:
            data['platform'] = platform_set['platform_name']

        data['currency'] = 'CNY'

        # 金额验证
        if params.get("total_amount", 0):
            data['total_fee'] = float(params.get("total_amount", 0)) * 100  # 元转分
        if data['total_fee'] < 1:
            return None, "支付金额不能小于一分钱"
        try:
            # 微信小程序支付
            if payment_method == "applets" or payment_method == "appletsv3":
                payment, err = PaymentWechatService.wechat_jsapi(data, "applets")
            # 公众号支付
            elif payment_method == "wechat_web":
                payment, err = PaymentWechatService.wechat_jsapi(data, "wechat_web")

            # 支付记录写入
            PaymentPayment.objects.create(**payment_data)
        except Exception as e:
            return None, str(e)

        if err:
            return None, err
        return payment, None

    @staticmethod
    def find(list, keyword):
        try:
            list.index(keyword)
            return True
        except ValueError:
            return False

    @staticmethod
    def ask_order_status(params):

        try:

            enroll_id = params.get("enroll_id", None)
            if not enroll_id:
                return None, "enroll_id不能为空"
            payment_set = PaymentPayment.objects.filter(**{"enroll_id": enroll_id}).order_by('-id')
            payment_set = payment_set.annotate(payment_status_name=F("payment_status__payment_status"),
                                               payment_code=F("payment_status__payment_code")).first()
            if not payment_set:
                return None, "查询不到该数据"
            payment_obj = model_to_dict(payment_set)
            PaymentStatus_set = PaymentStatus.objects.filter(**{"id": payment_obj['payment_status']}).first()
            PaymentStatus_obj = model_to_dict(PaymentStatus_set)
            return {
                       "status": PaymentStatus_obj['payment_code'],
                       "transact_no": payment_obj['transact_no'],
                       "order_no": payment_obj['order_no']
                   }, None
        except Exception as e:
            write_to_log(
                prefix="支付询单接口",
                content="报名id:" + str(enroll_id),
                err_obj=str(e)
            )
            return None, str(e)

    @staticmethod
    def format_dates(items, date_fields):
        for item in items:
            for field in date_fields:
                if field in item and item[field]:
                    try:
                        # 如果字段已经是 datetime 对象，就无需解析
                        if isinstance(item[field], datetime):
                            date = item[field]
                        else:
                            # 尝试解析并格式化日期
                            date = parse(item[field])
                        # 使用 strftime 格式化日期
                        item[field] = date.astimezone(tzlocal()).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # 如果解析失败，保留原来的值
                        pass
        return items

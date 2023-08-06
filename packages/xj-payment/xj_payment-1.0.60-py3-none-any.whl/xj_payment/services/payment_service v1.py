import logging
import random
from datetime import datetime

import pytz
import requests
import time

from django.core.paginator import Paginator
from django.db.models import F
from django.forms import model_to_dict
from django.utils import timezone
from pathlib import Path
from main.settings import BASE_DIR
from utils.custom_tool import format_params_handle
from xj_common.utils.custom_tool import format_list_handle
from xj_user.models import Platform
from xj_user.services.user_platform_service import UserPlatformService
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict
from xj_finance.services.finance_service import FinanceService
from xj_finance.services.finance_transact_service import FinanceTransactService
from xj_enroll.service.enroll_services import EnrollServices
from xj_thread.services.thread_item_service import ThreadItemService
from xj_user.services.user_service import UserService
from xj_payment.models import PaymentPayment
from xj_user.services.user_sso_serve_service import UserSsoServeService
from ..services.payment_wechat_service import PaymentWechatService

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))

sub_appid = main_config_dict.wechat_merchant_app_id or module_config_dict.wechat_merchant_app_id or ""
# 商户名称
merchant_name = main_config_dict.merchant_name or module_config_dict.merchant_name or ""


class PaymentService:
    @staticmethod
    def get(params):
        # def get(search_prams,search_params: dict = None, need_map: bool = False, filter_fields: list = None):

        # # 列表的查询参数处理
        # if filter_fields is None:
        #     filter_fields = ["id", "transact_no", "pay_mode", "nickname", "payment_status_id", "payment_status__payment_status", "register_time"]
        # else:
        #     filter_fields = format_list_handle(
        #         param_list=filter_fields,
        #         filter_filed_list=["id", "user_name", "full_name", "nickname", "phone", "email", "register_time"]
        #     )
        #     filter_fields = ["id", "user_name", "full_name", "nickname", "phone", "email",
        #                      "register_time"] if not filter_fields else filter_fields
        # # 字段查询参数处理
        # if search_params:
        #     search_params = format_params_handle(
        #         param_dict=search_params,
        #         filter_filed_list=["id", "user_id", "user_name", "full_name", "nickname", "phone", "email",
        #                            "create_time", "create_time_start", "create_time_end"],
        #         alias_dict={"user_id": "id", "register_time_start": "register_time__gte",
        #                     "register_time_end": "register_time_lte"}
        #     )

        limit = params.pop('limit', 20)
        page = params.pop('page', 20)

        list_obj = PaymentPayment.objects.filter(**params).order_by('-id')
        if params.get("create_time_start", None) and params.get("create_time_end", None):
            print(params.get("create_time_start", None))
            list_obj = list_obj.filter(
                create_time__range=(params['create_time_start'], params['create_time_end']))

        list_obj = list_obj.annotate(payment_status=F("payment_status__payment_status"), )

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

    # 支付总接口
    @staticmethod
    def pay(params):
        # print(params)
        data = params
        # data['total_fee'] = float(params['total_amount']) * 100  # 元转分
        payment_data = None
        out_trade_no = timezone.now().strftime('%Y%m%d%H%M%S') + ''.join(
            map(str, random.sample(range(0, 9), 4)))  # 随机生成订单号
        params['out_trade_no'] = out_trade_no
        if params['enroll_id']:
            enroll_data, err_txt = EnrollServices.enroll_detail(params['enroll_id'])  # 判断是否是报名订单
            if err_txt:
                return "报名记录不存在"
            data['enroll_id'] = enroll_data['id']
            data['user_id'] = enroll_data['user_id']
            data['total_fee'] = float(enroll_data['unpaid_amount']) * 100  # 元转分
        # 单点登录信息
        sso_data, err = UserSsoServeService.user_sso_to_user(data['user_id'], sub_appid)
        if err:
            return "单点登录记录不存在"
        sso_data = model_to_dict(sso_data)
        data['openid'] = sso_data['sso_unicode']
        tz = pytz.timezone('Asia/Shanghai')
        # 返回时间格式的字符串
        # now_time = timezone.now().astimezone(tz=tz)
        # now_time_str = now_time.strftime("%Y.%m.%d %H:%M:%S")
        # 返回datetime格式的时间
        now_time = timezone.now().astimezone(tz=tz).strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
        payment_data = {
            "order_no": out_trade_no,
            "enroll_id": data['enroll_id'],
            "user_id": data['user_id'],
            "total_amount": int(data['total_fee']),
            "create_time": now,
        }

        platform_set, err = UserPlatformService.payment_get_platform_info(params['platform_id'])
        if err:
            data['platform'] = merchant_name
        else:
            data['platform'] = platform_set['platform_name']

        data['currency'] = 'CNY'

        if params.get("total_amount", 0):
            data['total_fee'] = float(params.get("total_amount", 0)) * 100  # 元转分

        if data['total_fee'] < 1:
            return "支付金额不能小于一分钱"

        PaymentPayment.objects.create(**payment_data)
        # 支付方式检查
        if params['payment_method'] == "applets":  # 微信小程序支付

            payment = PaymentWechatService.payment_applets_pay(data)

        elif params['payment_method'] == "appletsv3":  # 微信小程序支付v3
            payment = PaymentWechatService.payment_applets_pay_v3(data)

        elif params['payment_method'] == "balance":  # 余额支付
            payment = PaymentWechatService.payment_balance_pay(data)
        else:
            payment = "支付方式不存在"

        return payment

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

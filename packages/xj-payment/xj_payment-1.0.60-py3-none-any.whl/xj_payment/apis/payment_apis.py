from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from ..utils.custom_tool import request_params_wrapper
from ..utils.user_wrapper import user_authentication_wrapper
from ..services.payment_service import PaymentService
from ..utils.custom_tool import flow_service_wrapper
from xj_user.services.user_service import UserService
from ..utils.model_handle import parse_data, util_response


class PaymentApis(APIView):

    # 支付列表
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def list(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("user_id", user_id)  # 用户ID
        params.setdefault("platform_id", platform_id)  # 平台
        data, err_txt = PaymentService.list(params)
        if err_txt:
            return util_response(err=47767, msg=err_txt)
        return util_response(data=data)

    # 支付总接口
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    @flow_service_wrapper
    def pay(self, *args, user_info, request_params, **kwargs, ):
        response = HttpResponse()
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("user_id", user_id)  # 用户ID
        params.setdefault("platform_id", platform_id)  # 平台
        data, err_txt = PaymentService.pay(params)
        if err_txt:
            if isinstance(err_txt, dict) and err_txt.get("error"):
                content = util_response(err=int(err_txt['error']), msg=err_txt['msg'])
            else:
                content = util_response(err=47767, msg=err_txt)
        else:
            content = util_response(data=data)
        response.content = content
        return response


    @require_http_methods(['GET'])
    @request_params_wrapper
    def ask_order_status(self, *args, request_params, **kwargs, ):
        params = request_params
        data, err_txt = PaymentService.ask_order_status(params)
        if err_txt:
            return util_response(err=47767, msg=err_txt)
        return util_response(data=data)

# encoding: utf-8
"""
@project: djangoModel->wechet_login
@author:
@created_time: 2022/7/14 10:55
"""
import uuid
# 微信登录方法
from logging import getLogger

from django.http import HttpResponse, response, JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from xj_user.services.wechat_service import WechatService
from ..services.login_service import LoginService
from ..utils.custom_tool import request_params_wrapper
from ..utils.user_wrapper import user_authentication_force_wrapper, user_authentication_wrapper
from ..services.user_main_service import UserMainService
from ..utils.custom_response import util_response

logger = getLogger('log')


class UserLoginMain(APIView):

    @require_http_methods(['POST'])
    @request_params_wrapper
    def login_main(self, *args, request_params=None, **kwargs):
        response = HttpResponse()
        response.status_code = 200
        if request_params is None:
            request_params = {}
        data, err = UserMainService.login_integration_interface(request_params)
        # data, err = WechatService.login_integration_interface(request_params)
        if err:
            if isinstance(err, dict) and err.get("error"):
                content = util_response(data=err['wechat_data'], msg=err['msg'], err=int(err['error']))
            else:
                content = util_response(err=4002, msg=err)
        else:
            content = util_response(data=data)
            response['Authorization'] = data.get("token", "")
        response.content = content
        return response

    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def bind_phone(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        bind_phone, err = LoginService.bind_phone(user_id, params.get("phone", ""))
        if err is None:
            return util_response(data=bind_phone)
        return util_response(err=47767, msg=err)

    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def secondary_authorization(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        params.setdefault("user_id", user_id)  # 用户ID
        empower, err = LoginService.secondary_authorization(params)
        if err is None:
            return util_response(data=empower)
        return util_response(err=47767, msg=err)

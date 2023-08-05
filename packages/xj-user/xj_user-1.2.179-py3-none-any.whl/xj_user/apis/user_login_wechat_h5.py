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

from xj_common.utils.custom_tool import request_params_wrapper
from xj_user.utils.user_wrapper import user_authentication_force_wrapper
from xj_user.utils.wechat import get_openid
from ..services.wechat_service import WechatService
from ..utils.custom_response import util_response
from ..utils.custom_tool import parse_data

logger = getLogger('log')


class WechetH5Login(APIView):

    @require_http_methods(['POST'])
    @request_params_wrapper
    def login_main(self, *args, request_params=None, **kwargs):
        response = HttpResponse()
        response.status_code = 200
        if request_params is None:
            request_params = {}
        data, err = WechatService.login_integration_interface(request_params)
        # if err:
        #     if isinstance(err, dict) and err.get("error"):
        #         return util_response(data=err['wechat_data'], msg=err['msg'], err=int(err['error']))
        #     return util_response(data=data)
        # return util_response(data=data)
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

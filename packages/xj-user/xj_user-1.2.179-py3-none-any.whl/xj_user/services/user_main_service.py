from django.forms import model_to_dict

from ..models import Platform
from ..services.login_service import LoginService


class UserMainService:
    """
     登录整合接口，支持以下几种登录方式：
          1、PASSWORD 账户密码登录
          2、SMS 短信验证码登录 （支持多账号登录*）
          3、WECHAT_APPLET 微信小程序授权登录
          4、WECHAT_WEB 微信公众号授权登录
          5、WECHAT_APP 微信APP授权登录

    """

    @staticmethod
    def login_integration_interface(params):
        # ----------------------------获取信息----------------------------------------
        # TODO platform_id字段 即将弃用，改为platform_code 20230507 by Sieyoo
        platform_id = params.get("platform_id", None)  # 平台。不应该支持ID传入，无法数据移植。20230507 by Sieyoo
        platform_code = params.get("platform_code", None)
        user_id = params.get("user_id", None)  # 用户id
        login_type = params.get("login_type", None)  # 支持的登录方式
        code = params.get("code", None)  # 微信登录code
        phone_code = params.get("phone_code", None)  # 微信手机号code
        sms_code = params.get("sms_code", None)  # 短信验证码
        sso_serve_id = params.get("sso_serve_id", 1)  # 单点登录用户平台
        phone = params.get("phone", None)  # 手机号
        other_params = params.get("other_params", None)
        account = params.get("account", None)  # 账户
        password = params.get("password", None)  # 密码
        bind_data = params.get("bind_data", None)  # 绑定的数据
        # ------------------------边界检查----------------------------------------------
        if not login_type:
            return None, "登录方式不能为空"

        if platform_code:
            platform_set = Platform.objects.filter(platform_code=platform_code).first()
            if not platform_set:
                return None, "platform不存在平台名称：" + platform_code
            platform_id = model_to_dict(platform_set)['platform_id']

        if platform_id:
            platform_set = Platform.objects.filter(platform_id=platform_id).first()
            if not platform_set:
                return None, "所属平台不存在"
            platform_code = model_to_dict(platform_set)['platform_code']

        # ------------------------登录类型判断----------------------------------------------

        if other_params is None:
            other_params = {}

        current_user, user_err = LoginService.type_judgment(login_type, account, phone, password, platform_code,
                                                            sms_code, user_id, code, phone_code,
                                                            sso_serve_id, bind_data)
        if user_err:
            return None, user_err
        if isinstance(current_user.get("user_info", None), list):
            return current_user, None
        else:
            data, err = LoginService.logical_processing(current_user.get("user_info", None),
                                                        current_user.get("phone", None), sso_serve_id,
                                                        current_user.get("appid", None),
                                                        current_user.get("openid", None),
                                                        current_user.get("unionid", None),
                                                        platform_id,
                                                        platform_code, other_params)
            if err:
                return None, err

        return data, None

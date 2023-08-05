# _*_coding:utf-8_*_

from django.urls import re_path

# from django.urls import include
# from django.views.generic import TemplateView
# from django.contrib.auth.decorators import login_required
from xj_user.apis.user_add import UserAdd
from xj_user.apis.user_login_main import UserLoginMain
from .apis import user_add
from .apis import user_contact_book
from .apis import user_detail_info
from .apis import user_edit
# from .apis import user_group
# from .apis import user_group_tree
from .apis import user_info
from .apis import user_list
from .apis import user_login
from .apis import user_login_short_message
from .apis import user_login_wechat
from .apis import user_password
from .apis import user_platform
from .apis import user_register
from .apis import user_relate_apis
from .apis import user_sso_serve
from .apis import user_statistics

# from .apis import user_short_message

# 应用名称
app_name = 'xj_user'

# 应用路由
urlpatterns = [
    # 平台相关API
    re_path(r'^platform/?$', user_platform.UserPlatform.as_view(), ),
    re_path(r'^platform_list/?$', user_platform.UserPlatform.list, ),
    re_path(r'^get_user_platform/?$', user_platform.UserPlatform.get_user_platform),  # 获取当前用户的平台信息

    re_path(r'^register/?$', user_register.UserRegister.as_view(), ),
    re_path(r'^login/?$', user_login.UserLogin.as_view(), ),
    re_path(r'^login_wechat/?$', user_login_wechat.WechetLogin.as_view(), ),
    # re_path(r'^login_wechat_app/?$', user_login_wechat_app.WechetAppLogin.as_view(), ),
    # re_path(r'^login_wechat_h5/?$', user_login_wechat_h5.WechetH5Login.as_view(), ),

    re_path(r'^list/?$', user_list.UserListAPIView.as_view(), ),  # 用户列表
    re_path(r'^info/?$', user_info.UserInfo.as_view(), ),
    re_path(r'^edit/?$', user_edit.UserEdit.user_edit, ),
    # re_path(r'^add/?$', user_add.UserAdd.as_view(), ),  # 管理员添加用户
    re_path(r'^delete/?$', user_edit.UserEdit.as_view(), ),  # 管理员添加用户

    re_path(r'^password/?$', user_password.UserPassword.as_view(), ),
    re_path(r'^contact_book/?$', user_contact_book.UserContactBook.as_view(), ),

    # 详细信息查询/新增/修改group_tree
    re_path(r'^list_detail/?$', user_detail_info.UserListDetail.as_view(), ),
    re_path(r'^detail/?$', user_detail_info.UserDetail.as_view(), ),
    # re_path(r'^detail_add/?$', user_detail_info.UserDetailAdd.as_view(), ),  # 用户必须存在才有信息编辑，所以这个接口是多余的
    re_path(r'^detail_edit/?$', user_detail_info.UserDetailEdit.as_view(), ),
    # re_path(r'^group_tree/?$', user_group_tree.UserGroupTree.as_view(), ),
    re_path(r'^detail_extend_fields/?$', user_detail_info.UserDetailExtendFields.as_view(), ),

    re_path(r'^add/?$', UserAdd.add, ),  # 管理员添加用户

    re_path(r'^login_main/?$', UserLoginMain.login_main, ),  #登录总接口

    re_path(r'^bind_phone/?$', UserLoginMain.bind_phone, ),  #绑定手机号

    re_path(r'^secondary_authorization/?$', UserLoginMain.secondary_authorization, ),  # 绑定手机号


    # 分组
    # re_path(r'^group/?$', user_group.GroupAPIView.as_view(), ),
    # re_path(r'^group_list/?$', user_group.GroupAPIView.list, ),

    # re_path(r'^send_message/?$', user_short_message.UserShortMessage.as_view(), ),
    # re_path(r'^login_short_message/?$', user_login_short_message.ShortMessageLogin.as_view(), ),
    re_path(r'^js_sdk/?$', user_sso_serve.UserSsoServe.get_js_sdk),  # 微信公众号JS-SDK
    re_path(r'^login_short_message/?$', user_login_short_message.ShortMessageLogin.sms_login),
    re_path(r'^login/?$', user_login.UserLogin.as_view(), ),
    re_path(r'^sso_serve/?$', user_sso_serve.UserSsoServe.as_view(), ),
    re_path(r'^statistics/?$', user_statistics.UserStatisticsAPI.as_view(), ),
    # 用户关系相关接口
    re_path(r'^relate_type/?$', user_relate_apis.UserRelateTypeApis.as_view(), ),
    re_path(r'^relate_user/?$', user_relate_apis.UserRelateToUserApis.as_view(), ),
]

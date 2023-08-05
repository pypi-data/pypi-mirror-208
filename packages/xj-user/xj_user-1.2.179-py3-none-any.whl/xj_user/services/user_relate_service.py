# encoding: utf-8
"""
@project: djangoModel->user_relate_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户关系服务
@created_time: 2022/12/13 16:45
"""
from django.core.paginator import Paginator
from django.db.models import F

from xj_role.services.role_service import RoleService
from ..models import UserRelateType, UserRelateToUser, BaseInfo
# 用户关系类型服务
from ..utils.custom_tool import format_params_handle, format_list_handle


class UserRelateTypeService():
    @staticmethod
    def list(params=None):
        if params is None:
            params = {}
        size = params.get("size", 10)
        page = params.get("page", 20)
        filter_params = format_params_handle(
            param_dict=params,
            filter_filed_list=["id", "relate_key", "relate_name", ]
        )
        relate_obj = UserRelateType.objects.filter(**filter_params).values()
        count = relate_obj.count()
        page_set = Paginator(relate_obj, size).get_page(page)
        return {'count': count, "page": page, "size": size, "list": list(page_set.object_list)}, None

    @staticmethod
    def add(params=None):
        if params is None:
            params = {}
        filter_params = format_params_handle(
            param_dict=params,
            filter_filed_list=["relate_key", "relate_name", "description"]
        )
        try:
            relate_obj = UserRelateType.objects.create(**filter_params)
            return {"id": relate_obj.id}, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def edit(pk=None, update_params=None):
        if update_params is None:
            update_params = {}
        filter_params = format_params_handle(
            param_dict=update_params,
            filter_filed_list=["relate_key", "relate_name", "description"]
        )
        if not pk or not filter_params:
            return None, "没有可修改的数据"
        try:
            relate_obj = UserRelateType.objects.filter(id=pk)
            if not relate_obj:
                return None, "没有可修改的数据"
            relate_obj.update(**filter_params)

            return None, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def delete(pk=None):
        if not pk:
            return None, "参数错误"
        relate_obj = UserRelateType.objects.filter(id=pk)
        if not relate_obj:
            return None, None
        try:
            relate_obj.delete()
        except Exception as e:
            return None, "删除异常:" + str(e)
        return None, None


# 用户关系映射服务
class UserRelateToUserService():
    @staticmethod
    def list(params=None, filter_fields=None):
        if filter_fields is None:
            filter_fields = ["user_id", "with_user_id", "relate_type_name", "user_name", "with_user_name"]
        if params is None:
            params = {}

        try:
            size = int(params.get("size", 10))
        except ValueError:
            size = 10
        try:
            page = int(params.get("page", 1))
        except ValueError:
            page = 1

        try:
            need_pagination = 1 if int(params.get("need_pagination", 1)) else 0
        except Exception as e:
            need_pagination = 1
        # 字段安全 过滤
        default_fields = [
            "user_id", "with_user_id", "user_relate_type_id", "relate_key", "relate_type_name",
            "user_name", "full_name", "nickname", "with_user_name", "with_full_name", "with_nickname"
        ]
        filter_fields = format_list_handle(
            param_list=filter_fields,
            filter_filed_list=default_fields
        )
        filter_params = format_params_handle(
            param_dict=params,
            filter_filed_list=["user", "user_id", "user_id_list", "with_user", "with_user_id", "user_relate_type", "user_relate_type_id", "relate_key"],
            alias_dict={"user_id_list": "user_id__in", "with_user_id_list": "with_user_id__in"}
        )
        relate_user_obj = UserRelateToUser.objects.annotate(
            relate_key=F("user_relate_type__relate_key"),
            relate_type_name=F("user_relate_type__relate_name"),
            user_name=F("user__user_name"),
            full_name=F("user__full_name"),
            nickname=F("user__nickname"),
            with_user_name=F("with_user__user_name"),
            with_full_name=F("with_user__full_name"),
            with_nickname=F("with_user__nickname"),
        ).filter(**filter_params).values(*filter_fields)

        count = relate_user_obj.count()
        if need_pagination:
            page_set = Paginator(relate_user_obj, size).get_page(page)
            return {'count': count, "page": page, "size": size, "list": list(page_set.object_list)}, None
        else:
            return list(relate_user_obj), None

    @staticmethod
    def add(params=None):
        if params is None:
            params = {}
        filter_params = format_params_handle(
            param_dict=params,
            filter_filed_list=["user", "user_id", "with_user", "with_user_id", "user_relate_type", "user_relate_type_id"],
            alias_dict={"user": 'user_id', "with_user": "with_user_id", "user_relate_type": "user_relate_type_id"}
        )
        if filter_params.get("user_id", None) is None or filter_params.get("with_user_id", None) is None or filter_params.get("user_relate_type_id", None) is None:
            return None, "参数错误"

        relate_user_obj = UserRelateToUser.objects.filter(
            user_id=filter_params['user_id'],
            with_user=filter_params['with_user_id'],
            user_relate_type_id=filter_params['user_relate_type_id']
        ).first()
        if relate_user_obj:
            return None, "该用户已经绑定，请勿重复绑定"

        try:
            relate_user_obj = UserRelateToUser.objects.create(**filter_params)
            return {"id": relate_user_obj.id}, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def edit(pk=None, params=None):
        if params is None:
            params = {}
        filter_params = format_params_handle(
            param_dict=params,
            filter_filed_list=["user", "user_id", "with_user", "with_user_id", "user_relate_type", "user_relate_type_id"],
            alias_dict={"user": 'user_id', "with_user": "with_user_id", "user_relate_type": "user_relate_type_id"}
        )
        if not pk or not params:
            return None, "没有可修改的数据"

        try:
            relate_user_obj = UserRelateToUser.objects.filter(id=pk)
            if not relate_user_obj:
                return None, "没有可修改的数据"
            relate_user_obj.update(**filter_params)
            return None, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def delete(pk=None):
        if not pk:
            return None, "参数错误"
        relate_user_obj = UserRelateToUser.objects.filter(id=pk)
        if not relate_user_obj:
            return None, None
        try:
            relate_user_obj.delete()
        except Exception as e:
            return None, "删除异常:" + str(e)
        return None, None

    @staticmethod
    def bind_bxtx_relate(params=None, user_info=None):
        """
        镖行天下绑定用户关系服务
        :param detail_params: 参数
        :param user_info: 用户信息
        :return: None,err_msg
        """
        # 绑定用户关系 邀请关系和收益关系
        if user_info is None:
            user_info = {}
        if params is None:
            params = {}

        inviter_id = params.get("inviter_id", None)
        print("邀请人ID：", inviter_id, "当前用户ID:", user_info.get('id', None))
        if not inviter_id:
            return None, "没有传递邀请人ID无法绑定邀请人"

        # 判断是否是一个有效的用户ID
        inviter = BaseInfo.objects.filter(id=inviter_id).first()
        if not inviter:
            return None, "没有该用户"
        data, err = UserRelateToUserService.add(
            {
                "user_id": user_info.get('id', None),
                "with_user_id": inviter_id,
                "user_relate_type_id": 1
            }
        )
        if err:
            return None, err

        # 邀请人不存在受益人，如果邀请人是业务，则绑定的受益人也是该邀请人
        res, err = RoleService.is_this_role(user_id=inviter_id, role_key="BID-SALESMAN")  # 如果是业务人员
        if res:
            data, err = UserRelateToUserService.add(
                {
                    "user_id": user_info.get('id', None),
                    "with_user_id": inviter_id,
                    "user_relate_type_id": 2
                }
            )
            return None, None

        # 查询邀请人的受益人是谁，如果存在则绑定。
        saler = UserRelateToUser.objects.filter(user_id=inviter_id, user_relate_type_id=2).first()
        if saler:
            data, err = UserRelateToUserService.add(
                {
                    "user_id": user_info.get('id', None),
                    "with_user_id": inviter_id,
                    "user_relate_type_id": 2
                }
            )
            return None, None
        return None, None

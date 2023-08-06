# encoding: utf-8
"""
@project: djangoModel->user_permission_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户权限服务
@created_time: 2022/8/23 9:33
"""
from typing import AnyStr, List, Dict, Tuple, Any, SupportsInt, SupportsFloat

from django.core.paginator import Paginator
from django.db.models import F

from xj_role.utils.model_handle import format_params_handle
from ..models import RolePermissionValue, UserToRole, Role, RolePermission
from ..services.role_service import RoleTreeService, RoleService
from ..utils.j_dict import JDict
from ..utils.j_recur import JRecur


# 权限值服务
class PermissionValueService():
    @staticmethod
    def add_permission_value(params):
        """添加权限值"""
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["permission_id", "module", "feature", "permission_value", "type", "relate_key",
                               "relate_value", "config",
                               "is_enable", "is_system", "is_ban", "ban_view", "ban_edit", "ban_add", "ban_delete",
                               "description"]
        )
        if not params:
            return None, "参数不能为空"
        instance = RolePermissionValue.objects.create(**params)
        return {"id": instance.id}, None

    @staticmethod
    def del_permission_value(id):
        # 删除权限值
        if not id:
            return None, "ID 不可以为空"
        instance = RolePermissionValue.objects.filter(id=id)
        if instance:
            instance.delete()
        return None, None

    @staticmethod
    def edit_permission_value(params):
        # 编辑权限值
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["id", "permission_id", "module", "feature", "permission_value", "type", "relate_key",
                               "relate_value", "config",
                               "is_enable", "is_system", "is_ban", "ban_view", "ban_edit", "ban_add", "ban_delete",
                               "description"]
        )
        print(params)
        id = params.pop("id", None)
        if not id:
            return None, "ID 不可以为空"
        if not params:
            return None, "没有可以修改的字段"
        instance = RolePermissionValue.objects.filter(id=id)
        try:
            instance.update(**params)
        except Exception as e:
            return None, "编辑权限错误：" + str(e)
        return None, None

    @staticmethod
    def list(params):
        page = params.pop("page", 1)
        size = params.pop("size", 20)
        params = format_params_handle(param_dict=params,
                                      filter_filed_list=["id", "page", "size", "module", "feature", "permission_id"])
        query_set = RolePermissionValue.objects.filter(**params).annotate(
            permission_name=F("permission__permission_name")).annotate(
            permission_description=F("permission__description"))
        count = query_set.count()
        query_list = query_set.values() if query_set else []
        finish_set = list(Paginator(query_list, size).page(page).object_list)
        return {"count": count, "page": int(page), "size": int(size), "list": finish_set}, None


# 权限服务
class PermissionService:
    @staticmethod
    def add_permission(params):
        """添加权限值"""
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["permission_id", "permission_name", "description"]
        )
        if not params:
            return None, "参数不能为空"
        RolePermission.objects.create(**params)
        return None, None

    @staticmethod
    def del_permission(permission_id):
        # 删除权限值
        if not permission_id:
            return None, "permission_id 不可以为空"
        instance = RolePermission.objects.filter(permission_id=permission_id)
        if instance:
            instance.delete()
        return None, None

    @staticmethod
    def edit_permission(params):
        # 编辑权限值
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["permission_id", "permission_name", "description"]
        )
        permission_id = params.pop("permission_id", None)
        if not permission_id:
            return None, "ID 不可以为空"
        if not params:
            return None, "没有可以修改的字段"
        instance = RolePermission.objects.filter(permission_id=permission_id)
        try:
            instance.update(**params)
        except Exception as e:
            return None, "编辑权限错误：" + str(e)
        return None, None

    @staticmethod
    def list(params):
        page = params.pop("page", 1)
        size = params.pop("size", 20)
        params = format_params_handle(param_dict=params,
                                      filter_filed_list=["permission_id", "permission_name", "description"])
        query_set = RolePermission.objects.filter(**params)
        count = query_set.count()
        query_list = query_set.values() if query_set else []
        finish_set = list(Paginator(query_list, size).page(page).object_list)
        return {"count": count, "page": int(page), "size": int(size), "list": finish_set}, None

    @staticmethod
    def get_role_tree_relate_user(user_id):
        user_role_obj = UserToRole.objects.filter(user_id=user_id).annotate(
            parent_role_id=F("role__parent_role_id"))  # 找到用户的角色ID列表，用于判断同角色，子角色，父角色
        user_roles = user_role_obj.values() if user_role_obj else []
        # print("user_roles:", user_roles)
        u_role_ids = [i['role_id'] for i in user_roles]  # 同组
        p_role_ids = [i['parent_role_id'] for i in user_roles]  # 父组

        c_role_set = Role.objects.filter(parent_role_id__in=u_role_ids)
        c_roles = c_role_set.values() if c_role_set else []
        c_role_ids = [i['id'] for i in c_roles]  # 子组
        res_set = {
            "GROUP_INSIDE": list(
                set([i['user_id'] for i in list(UserToRole.objects.filter(role_id__in=u_role_ids).values("user_id"))])),
            "GROUP_PARENT": list(
                set([i['user_id'] for i in list(UserToRole.objects.filter(role_id__in=p_role_ids).values("user_id"))])),
            "GROUP_CHILDREN": list(
                set([i['user_id'] for i in list(UserToRole.objects.filter(role_id__in=c_role_ids).values("user_id"))])),
            "GROUP_OUTSIDE": []
        }
        return res_set, None

    @staticmethod
    def user_permission_tree(user_id, module=None, feature=None, feature_list=None, debug=False):
        """
        获取用户的权限值
        @param user_id 用户ID
        @param module 模块名
        @param feature 功能名
        @param feature_list 功能列表
        @param debug 调试模式会返回更多的权限信息
        """
        # print("> user_permission_group:", user_id, module, feature, feature_list, debug)
        try:
            # 获取用户的权限(组)
            user_to_role_set = UserToRole.objects.filter(user_id=user_id) \
                .annotate(user_permission_id=F("role__permission_id"))
            if not user_to_role_set:
                return {}, None
            user_role_list = list(user_to_role_set.values())
            # print("> user_role_list:", user_role_list)
            user_permission_id_list = [it.user_permission_id for it in user_to_role_set]
            # print("> user_permission_id_list:", user_permission_id_list)

            # 获取用户的权限值，注：一个用户可能属于多个角色并有多种权限
            permission_value_set = RolePermissionValue.objects.all()
            if module:
                permission_value_set = permission_value_set.filter(module=module)
            if feature:
                permission_value_set = permission_value_set.filter(feature=feature)
            if feature_list:
                permission_value_set = permission_value_set.filter(feature__in=feature_list)
            permission_value_set = permission_value_set.filter(permission_id__in=user_permission_id_list)
            if not permission_value_set:
                return {}, None
            group_user, err = PermissionService.get_role_tree_relate_user(user_id)
            permission_value_list = list(permission_value_set.values(
                "id", "permission_id", "module", "feature", "permission_value", "flag", "relate_key", "relate_value",
                'config', 'is_enable', "is_system", "is_ban", "ban_view", "ban_edit", "ban_add", "ban_delete",
                'description'
            ))
            # print("> permission_value_list:", len(permission_value_list), permission_value_list)

            # 按 module>feature>permission_value，三级进行字典嵌套
            permission_tree = JDict({})
            for permission_dict in permission_value_list:
                value_list = permission_dict.get('permission_value', '').split(';')
                it = JDict(permission_dict)
                for vv in value_list:
                    if type(vv) == str:
                        vv = vv.strip()
                    if not permission_tree[it.module]:
                        permission_tree[it.module] = {}
                    if not permission_tree[it.module][it.feature]:
                        permission_tree[it.module][it.feature] = {}
                    if not vv:
                        vv = str(it.id)
                    if not permission_tree[it.module][it.feature][vv]:
                        permission_tree[it.module][it.feature][vv] = {}
                    if not it.flag:
                        it.flag = str(it.id)

                    repeat_permission_list = []
                    # 这里开始复杂了，如有同名权限，说明用户有多个角色，需要对权限叠加
                    if permission_tree[it.module][it.feature][vv][it.flag]:
                        old = permission_tree[it.module][it.feature][vv][it.flag]
                        # print("> old:", old)
                        # print("> it1:", it)
                        repeat_permission_list.append({'repeat_1': old, 'repeat_2': it})
                        if it.is_enable and it.is_ban != 'Y':  # 新权限启用且没有全部禁止才进入两组判断
                            it.ban_view = 'N' if it.ban_view != 'Y' or old.ban_view != 'Y' else 'Y'
                            it.ban_edit = 'N' if it.ban_edit != 'Y' or old.ban_edit != 'Y' else 'Y'
                            it.ban_add = 'N' if it.ban_add != 'Y' or old.ban_add != 'Y' else 'Y'
                            it.ban_delete = 'N' if it.ban_delete != 'Y' or old.ban_delete != 'Y' else 'Y'
                        # print("> it2:", it)

                    it["user_list"] = group_user.get(vv, [])
                    permission_tree[it.module][it.feature][vv][it.flag] = it

        except Exception as e:
            # print("msg:" + str(e) + " line:" + str(e.__traceback__.tb_lineno))
            return None, "msg: " + str(e) + ", line: " + str(e.__traceback__.tb_lineno)
        # print("> permission_tree:", permission_tree)

        if debug:
            return {'permission_tree': permission_tree, 'user_role_list': user_role_list,
                    'repeat_permission_list': repeat_permission_list}, None

        return permission_tree, None


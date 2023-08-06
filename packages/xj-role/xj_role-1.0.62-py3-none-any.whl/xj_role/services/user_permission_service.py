# encoding: utf-8
"""
@project: djangoModel->user_permission_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户权限服务
@created_time: 2022/8/23 9:33
"""
from django.db.models import F

from ..models import RolePermissionValue, UserToRole, Role
from ..utils.j_dict import JDict


class PermissionService():
    __user_dict = None
    __is_err = False
    __err_message = None

    @staticmethod
    def get_group_user(user_id):
        user_role_obj = UserToRole.objects.filter(user_id=user_id).annotate(p_role_id=F("role__parent_role_id"))  # 找到用户的角色ID列表，用于判断同角色，子角色，父角色
        user_roles = user_role_obj.values() if user_role_obj else []
        u_role_ids = [i['role_id'] for i in user_roles]  # 同组
        p_role_ids = [i['p_role_id'] for i in user_roles]  # 父组

        c_role_obj = Role.objects.filter(parent_role_id__in=u_role_ids)
        c_roles = c_role_obj.values() if c_role_obj else []
        c_role_id = [i['id'] for i in c_roles]  # 子组
        res_set = {
            "GROUP_INSIDE": list(set([i['user_id'] for i in list(UserToRole.objects.filter(role_id__in=u_role_ids).values("user_id"))])),
            "GROUP_PARENT": list(set([i['user_id'] for i in list(UserToRole.objects.filter(role_id__in=p_role_ids).values("user_id"))])),
            "GROUP_CHILDREN": list(set([i['user_id'] for i in list(UserToRole.objects.filter(role_id__in=c_role_id).values("user_id"))])),
            "GROUP_OUTSIDE": []
        }
        return res_set, None

    @staticmethod
    def get_user_group_permission(user_id, module=None, feature="ROLE_GROUP", type=None):
        try:
            # 获取用户的权限
            params = {k: v for k, v in {"module": module, "feature": feature}.items() if v}
            permission_set = UserToRole.objects.filter(user_id=user_id).annotate(user_permission_id=F("role__permission_id")).values()
            if not permission_set:
                return {}, None
            permission_dict = [i['user_permission_id'] for i in list(permission_set.values("user_permission_id"))]
            params.setdefault("permission_id__in", list(set(permission_dict)))
            values = list(RolePermissionValue.objects.filter(**params).values(
                "module", "permission_value", "relate_value", "ban_view", "ban_edit", "ban_add", "ban_delete", "is_ban", "is_system", 'is_enable'
            ))
            if not values:
                return {}, None
            res = JDict({})
            group_user, err = PermissionService.get_group_user(user_id)
            for item in values:
                item_copy = JDict(item)
                module_name = item_copy.pop('module')
                res.setdefault(module_name, {})

                current_module = getattr(res, module_name)
                current_module.setdefault('relate_value', item_copy.pop("relate_value"))

                permission_value = item_copy.pop('permission_value')
                item_copy["user_list"] = group_user[permission_value] if permission_value in group_user.keys() else []
                current_module.setdefault(permission_value, item_copy)
            res = res[module] if module else res
            return res, None
        except Exception as e:
            print("msg:" + str(e) + "line:" + str(e.__traceback__.tb_lineno))
            return None, "msg:" + str(e) + "line:" + str(e.__traceback__.tb_lineno)


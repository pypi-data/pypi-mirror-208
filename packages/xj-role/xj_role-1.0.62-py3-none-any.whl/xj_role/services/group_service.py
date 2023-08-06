# encoding: utf-8
"""
@project: djangoModel->group_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户组（部门服务）
@created_time: 2022/9/5 11:33
"""

from django.core.paginator import Paginator

from xj_role.services.role_service import RoleService
from xj_user.services.user_service import UserService
from ..models import UserToGroup, RoleUserGroup
from ..utils.model_handle import format_params_handle, parse_json


# 用户组 树状数据返回
class GroupTreeService(object):
    @staticmethod
    def getTree(data_list, parent_group):
        tree = []
        for item in data_list:
            if str(item['parent_group_id']) == str(parent_group):
                id(item)
                item['name'] = item['group_name']
                item['is_group'] = True
                children = GroupTreeService.getTree(data_list, item['id'])
                if children:
                    item['children'] = children
                tree.append(item)
        return tree

    @staticmethod
    def getTrees(data_list, parent_group):
        tree = []
        if parent_group != 0:
            base_node = RoleUserGroup.objects.filter(id=parent_group).to_json()
            for item in data_list:
                if str(item['parent_group_id']) == str(parent_group):
                    item['name'] = item['group_name']
                    item['children'] = GroupTreeService.getTree(data_list, item['id'])
                    tree.append(item)
            base_node[0]['children'] = tree
            return base_node[0]
        else:
            # 默认不需要搜索
            for item in data_list:
                if not str(item['parent_group_id']) == str(parent_group):
                    continue
                child = GroupTreeService.getTree(data_list, item['id'])
                if child:
                    item['name'] = item['group_name']
                    item['children'] = child
                    tree.append(item)
        return tree

    @staticmethod
    def group_tree(group_id=0):
        data_list = RoleUserGroup.objects.filter().to_json()
        group_tree = GroupTreeService.getTrees(data_list, group_id)
        return group_tree, None


# 用户组CURD服务
class GroupService(object):
    @staticmethod
    def get_user_from_group(group_id):
        """根据用户组ID获取用户ID列表"""
        user_obj = UserToGroup.objects.filter(user_group_id=group_id)
        user_list = []
        if user_obj:
            user_list = user_obj.values("user_id")
            user_list = [i['user_id'] for i in user_list]
        return user_list, None

    @staticmethod
    def group_tree_role(params):
        # 分组角色树
        group_id = params.get("group_id", 0)
        tree_data, err = GroupTreeService.group_tree(group_id)
        if err:
            return None, err
        role_list, err = RoleService.get_role_list({}, None)
        role_dict = {}
        for role in role_list:
            index = str(role['user_group_id'])
            if index not in role_dict.keys():
                role_dict[index] = []
            role_dict[index].append(role)

        def parse_tree(tree, parent_group_id=None):
            for item in tree:
                if "children" not in item.keys():
                    item['children'] = []
                if len(item['children']) > 0:
                    parse_tree(item['children'], item["id"])
                if str(item['id']) in role_dict.keys():
                    print("> role_dict:", role_dict[str(item['id'])])
                    item['children'].extend(role_dict[str(item['id'])])
            return tree

        return parse_tree(parse_json(tree_data), 0), None

    @staticmethod
    def group_tree_user(params):
        # 分组用户树
        group_id = params.get("group_id", 0)
        tree_data, err = GroupTreeService.group_tree(group_id)
        if err:
            return None, err
        user_group_obj = UserToGroup.objects
        if group_id:
            user_group_set = user_group_obj.filter(user_group_id=group_id)
        else:
            user_group_set = user_group_obj.all()
        user_group_dict = {str(item["user_id"]): str(item['user_group_id']) for item in list(user_group_set.values())} if user_group_set else {}
        user_list, err = UserService.user_list({"id__in": user_group_dict.keys()}, None)
        group_user_dict = {}
        for user in user_list:
            index = user_group_dict.get(str(user['id']), None)
            if not index:
                continue
            if index not in group_user_dict.keys():
                group_user_dict[index] = []
            user["group_id"] = index
            group_user_dict[index].append(user)

        def parse_tree(tree, parent_group_id=None):
            for item in tree:
                if "children" not in item.keys():
                    item['children'] = []
                if len(item['children']) > 0:
                    parse_tree(item['children'], item["id"])
                if str(item['id']) in group_user_dict.keys():
                    item['children'].extend(group_user_dict[str(item['id'])])
            return tree

        return parse_tree(parse_json(tree_data), 0), None

    @staticmethod
    def user_bind_group(user_id, group_id):
        # 用户绑定部门
        if not user_id or not group_id:
            return None, "参数错误，user_id, group_id 必传"
        try:
            UserToGroup.objects.get_or_create(
                {"user_id": user_id, "group_id": group_id},
                user_id=user_id,
                group_id=group_id,
            )
            return None, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def group_list(params):
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=["page", "size", "group", "group_name", "parent_group_id"],
            alias_dict={"group_name": "group_name__contains"}
        )
        page = params.pop("page", 1)
        size = params.pop("size", 20)
        group_set = RoleUserGroup.objects.filter(**params)
        count = group_set.count()
        group_list = group_set.values()
        finish_set = list(Paginator(group_list, size).page(page))
        return {"page": int(page), "size": int(size), "count": int(count), "list": finish_set}, None

    @staticmethod
    def add_group(params):
        params = format_params_handle(param_dict=params, filter_filed_list=["group", "group_name", "parent_group_id", "description"])
        if not params:
            return None, "参数不能为空"
        instance = RoleUserGroup.objects.create(**params)
        return {"id": instance.id}, None

    @staticmethod
    def edit_group(params):
        params = format_params_handle(param_dict=params, filter_filed_list=["id", "group", "group_name", "parent_group_id", "description"])
        id = params.pop("id", None)
        if not id:
            return None, "ID 不可以为空"
        if not params:
            return None, "没有可以修改的字段"
        instance = RoleUserGroup.objects.filter(id=id)
        if params:
            instance.update(**params)
        return None, None

    @staticmethod
    def del_group(id):
        if not id:
            return None, "ID 不可以为空"
        instance = RoleUserGroup.objects.filter(id=id)
        if instance:
            instance.delete()
        return None, None

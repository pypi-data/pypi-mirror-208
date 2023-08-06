# _*_coding:utf-8_*_

from django.urls import re_path

from .apis.group_api import GroupAPIView
from .apis.permission_api import PermissionValueAPIView, PermissionAPIView
from .apis.role_api import RoleAPIView
from .service_register import register

app_name = 'xj_role'

register()

# 应用路由
urlpatterns = [
    # 角色相关接口
    re_path(r'^list/?$', RoleAPIView.list),  # 角色分页列表
    re_path(r'^tree/?$', RoleAPIView.tree),  # 角色树
    re_path(r'^role/?(?P<id>\d+)?$', RoleAPIView.as_view()),  # 角色 增加（post）/删除(delete)/修改(edit)
    re_path(r'^user_role_users/?$', RoleAPIView.user_role_users),  # 角色 用户列表

    # 权限API
    re_path(r'^permission_list/?', PermissionAPIView.list, ),  # 根据分组ID,获取绑定用户ID，测试接口
    re_path(r'^permission/?(?P<permission_id>\d+)?$', PermissionAPIView.as_view()),  # 分组 角色树
    # 权限值相关接口
    re_path(r'^permission_value_list/?$', PermissionValueAPIView.list, ),  # 权限值列表
    re_path(r'^permission_value/?(?P<id>\d+)?$', PermissionValueAPIView.as_view(), ),  # 权限值增删改
    re_path(r'^user_permission_tree/?$', PermissionValueAPIView.get_user_permission_tree, ),  # 用户权限判断

    # 用户组相关的接口
    re_path(r'^group/?(?P<user_group_id>\d+)?$', GroupAPIView.as_view()),  # 分组 增加（post）/删除(delete)/修改(edit)
    re_path(r'^user_group_list/?$', GroupAPIView.user_group_list),  # 用户分组列表
    re_path(r'^get_user_ids_by_group/(?P<user_group_id>\d+)?$', GroupAPIView.get_user_ids_by_group),  # 根据分组ID获取用户ID

    re_path(r'^in_group_users/?$', GroupAPIView.in_group_users),  # 分组里面所有的用户 用户列表,支持用户的搜索
    re_path(r'^user_group_users/?$', GroupAPIView.in_group_users),  # 分组里面所有的用户 用户列表,支持用户的搜索

    re_path(r'^user_group_tree/?$', GroupAPIView.user_group_tree),
    re_path(r'^group_tree_role/?$', GroupAPIView.group_tree_role),  # 分组 角色树 # 用户分组树，原为role_group_tree，命名难以理解，改为role_user_group_tree
    re_path(r'^group_tree_user/?$', GroupAPIView.group_tree_user),  # 分组 用户树

    # 用户分组和用户角色的多对多映射关系
    re_path(r'^group_user_detail/?$', GroupAPIView.group_user_detail),  # 用户分组和用户角色关系和用户详情联合返回
    re_path(r'^group_user_add/?$', GroupAPIView.group_user_add),  # 用户分组和用户角色关系添加 为什么要添加用户呢?不应该绑定用户关系
    re_path(r'^group_user_edit/?$', GroupAPIView.group_user_edit),  # 用户分组和用户角色关系修改
    # re_path(r'^bind_user_role/?$', GroupAPIView.bind_user_role),  # 用户角色那绑定
    re_path(r'^bind_user_group/?$', GroupAPIView.user_bind_groups),  # 用户分组绑定
]

# encoding: utf-8
"""
@project: djangoModel->role_api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 角色API
@created_time: 2022/9/2 15:38
"""
from rest_framework.views import APIView

from ..services.role_service import RoleService, RoleTreeService
from ..utils.custom_tool import request_params_wrapper
from ..utils.model_handle import *


class RoleAPIView(APIView):

    @request_params_wrapper
    def user_role_users(self, *args, request_params, **kwargs):
        """查询属于该角色的用户列表"""
        data, err = RoleService.user_role_users(
            params=request_params,
            is_subtree=request_params.get("is_subtree"),
            without_user_info=request_params.get("without_user_info"),
        )
        if err:
            return util_response(err=2000, msg=err)
        return util_response(data=data)

    def tree(self):
        """角色树接口"""
        params = parse_data(self)
        res, err = RoleTreeService.role_tree(role_id=params.get("role_id", 0), role_key=params.get("role_key", None))
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=res)

    @request_params_wrapper
    def list(self, *args, request_params, **kwargs):
        """角色列表"""
        data, err = RoleService.get_role_list(
            params=request_params,
            need_pagination=True,
            filter_fields=request_params.pop("filter_fields", None)
        )
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def put(self, request, **kwargs):
        # 角色 修改接口
        params = parse_data(request)
        params.setdefault("id", kwargs.get("role_id", None))
        data, err = RoleService.edit_role(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def post(self, request, **kwargs):
        # 角色 添加接口
        params = parse_data(request)
        data, err = RoleService.add_role(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def delete(self, request, **kwargs):
        # 角色 删除接口
        id = parse_data(request).get("id", None) or kwargs.get("role_id")
        if not id:
            return util_response(err=1000, msg="id 必传")
        data, err = RoleService.del_role(id)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

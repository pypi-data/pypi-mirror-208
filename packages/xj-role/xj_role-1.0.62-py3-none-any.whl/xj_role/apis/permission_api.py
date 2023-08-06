# encoding: utf-8
"""
@project: djangoModel->user_auth
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户权限API
@created_time: 2022/8/23 9:16
"""
from rest_framework.views import APIView

from xj_user.services.user_service import UserService
from ..services.permission_service import PermissionService, PermissionValueService
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_data


class PermissionValueAPIView(APIView):
    def post(self, request):
        # 权限添加
        params = parse_data(request)
        data, err = PermissionValueService.add_permission_value(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def delete(self, request, **kwargs):
        # 权限删除
        id = parse_data(request).get("id") or kwargs.get("id", None)
        if not id:
            return util_response(err=1000, msg="permission_id 不可以为空")
        data, err = PermissionValueService.del_permission_value(id)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    def put(self, request, **kwargs):
        # 权限修改
        params = parse_data(request)
        # 参数补全
        id = params.get("id") or kwargs.get("id", None)
        if not id:
            return util_response(err=1000, msg="id 不可以为空")
        params.setdefault("id", id)

        data, err = PermissionValueService.edit_permission_value(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def list(self):
        # 列表
        params = parse_data(self)
        data, err = PermissionValueService.list(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)


    def get_user_permission_tree(self):
        # 判断用户是否有权限
        params = parse_data(self)
        module = params.get("module", '').upper() or None
        feature = params.get("feature", '').upper() or None
        feature_list = feature.split(';') if feature else None
        debug = params.get("debug", False)
        token = self.META.get('HTTP_AUTHORIZATION', None)
        token_serv, error_text = UserService.check_token(token)
        # print("> get_user_permission_tree:", module, feature, debug)
        if error_text:
            return util_response(err=6558, msg=error_text)
        data, error_text = PermissionService.user_permission_tree(token_serv['user_id'], module=module,
                                                                  feature_list=feature_list, debug=debug)
        if error_text:
            return util_response(err=1000, msg=error_text)
        return util_response(data=data)


class PermissionAPIView(APIView):
    def post(self, request):
        # 权限添加
        params = parse_data(request)
        data, err = PermissionService.add_permission(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def delete(self, request, **kwargs):
        # 权限删除
        permission_id = parse_data(request).get("permission_id") or kwargs.get("permission_id", None)
        if not permission_id:
            return util_response(err=1000, msg="permission_id 不可以为空")
        data, err = PermissionService.del_permission(permission_id)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    def put(self, request, **kwargs):
        # 权限修改
        params = parse_data(request)
        # 参数补全
        permission_id = params.get("permission_id") or kwargs.get("permission_id", None)
        if not id:
            return util_response(err=1000, msg="id 不可以为空")
        params.setdefault("permission_id", permission_id)

        data, err = PermissionService.edit_permission(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    def list(self):
        # 列表
        params = parse_data(self)
        data, err = PermissionService.list(params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

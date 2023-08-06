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
from ..services.user_permission_service import PermissionService
from ..utils.custom_response import util_response


class UserPermissions(APIView):
    def get(self, request):
        module = request.query_params.get("module", "thread").lower()
        feature = request.query_params.get("feature", "ROLE_GROUP").upper()
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token:
            token_serv, error_text = UserService.check_token(token)
            if error_text:
                return util_response(err=6558, msg=error_text)
            data, err_text = PermissionService.get_user_group_permission(token_serv['user_id'], module, feature)

            return util_response(data=data)
        return util_response()

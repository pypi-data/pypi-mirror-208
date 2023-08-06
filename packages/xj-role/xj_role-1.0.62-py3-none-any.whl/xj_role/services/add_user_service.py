# encoding: utf-8
"""
@project: djangoModel->add_user_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 用户联动服务
@created_time: 2022/9/2 9:53
"""
from ..models import UserToGroup, UserToRole


class UserLinkageService():

    # 添加用户
    @staticmethod
    def add_user(user_id, user_group_id=None, role_id=None):
        if user_group_id:
            UserToGroup.objects.create(user_id=user_id, user_group_id=user_group_id)
        if role_id:
            UserToRole.objects.create(user_id=user_id, role_id=role_id)
        return None, None

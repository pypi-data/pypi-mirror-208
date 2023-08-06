from django.contrib import admin

# 引入用户平台
from .models import *


class PermissionAdmin(admin.ModelAdmin):
    fields = ('permission_id', 'permission_name', 'description')
    list_display = ('permission_id', 'permission_name', 'description')
    readonly_fields = ['permission_id']


class PermissionValueAdmin(admin.ModelAdmin):
    fields = (
        'id', 'permission', 'module', 'feature', 'permission_value', 'flag', 'relate_key', 'relate_value', 'config',
        'is_enable', 'is_system', 'is_ban', 'ban_view', 'ban_edit', 'ban_add', 'ban_delete', 'description')
    list_display = (
        "id", "permission", "module", "feature", "permission_value", 'flag', "relate_key", "short_relate_value", 'short_config',
        'is_enable', "is_system", "is_ban", "ban_view", "ban_edit", "ban_add", "ban_delete", 'description')
    readonly_fields = ['id']


class GroupAdmin(admin.ModelAdmin):
    fields = ('id', 'group', 'group_name', 'parent_group_id', 'description')
    list_display = ('id', 'group', 'group_name', 'parent_group_id', 'description')
    readonly_fields = ['id']


class RoleAdmin(admin.ModelAdmin):
    fields = ('id', 'role', 'role_name', 'parent_role_id', "permission", 'user_group', 'description')
    list_display = ('id', 'role', 'role_name', 'parent_role_id', "permission", 'description')
    readonly_fields = ['id']


class UserToGroupAdmin(admin.ModelAdmin):
    fields = ('id', 'user_id', 'user_group')
    list_display = ('id', 'user_id', 'user_group')
    readonly_fields = ['id']


class UserToRoleAdmin(admin.ModelAdmin):
    fields = ('id', 'user_id', 'role')
    list_display = ('id', 'user_id', 'role')
    readonly_fields = ['id']


admin.site.register(RolePermission, PermissionAdmin)
admin.site.register(RolePermissionValue, PermissionValueAdmin)
admin.site.register(RoleUserGroup, GroupAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserToGroup, UserToGroupAdmin)
admin.site.register(UserToRole, UserToRoleAdmin)

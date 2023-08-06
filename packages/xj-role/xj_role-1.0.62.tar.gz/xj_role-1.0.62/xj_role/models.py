from django.db import models


# Create your models here.


class RolePermission(models.Model):
    """ 5、Role_RolePermission 权限组表 """
    permission_id = models.IntegerField(verbose_name='权限ID', primary_key=True, help_text='必填。不自动生成，由运营人员统一设置。')
    permission_name = models.CharField(verbose_name='权限名称', max_length=255, blank=True, null=True, help_text='权限名称')
    description = models.CharField(verbose_name='权限描述', max_length=255, blank=True, null=True, help_text='权限描述')

    class Meta:
        db_table = 'role_permission'
        verbose_name_plural = "05. 角色 - 权限组表"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.permission_name}"


class RolePermissionValue(models.Model):
    """
    6、Role_RolePermissionValue 角色组值表 [1-N]
    权限标识值，一个permission_id可以对应多个value，多值形成一组权限。值为宏名，需要多语言翻译
    """
    module_choices = [
        ('USER', '用户'),
        ('THREAD', '信息'),
        ('COMMENT', '评论'),
        ('FINANCE', '资金'),
        ('ENROLL', '报名'),
        ('RESOURCE', '资源'),
        ('DICTIONARY', '字典'),
        ('PAYMENT', '支付'),
        ('ROLE', '角色'),
    ]
    feature_choices = [
        ('OTHER_ROLE_OPERATE', '按其他角色操作'),
        ('SELF_ROLE_OPERATE', '按本人角色操作'),
        ('CATEGORY_NAME', '按类别名称'),
        ('CATEGORY_FIELD', '按类别字段'),
        ('ROUTE', '按路由'),
        ('FIELD', '按字段'),
    ]
    flag_choices = [
        ('ALL', '全部'),
        ('SUPER_ADMINISTRATOR', '超级管理员可操作'),  # 超级管理员。整个数据库的全部数据
        ('ADMINISTRATOR', '管理员可操作'),  # 管理员。所属角色“树根”下的全部数据，即平台
        ('MANAGER', '主管可操作'),  # 管理员。所属角色“所在树”下的全部数据，即平台
        ('ROLE_OUTSIDE', '外部角色可操作'),
        ('ROLE_INSIDE', '同级角色可操作'),
        ('ROLE_PARENT', '上级角色可操作'),
        ('ROLE_CHILDREN', '下级角色可操作'),
        ('MANAGER_OUTSIDE', '主管-可操作外部'),
        ('MANAGER_INSIDE', '主管-可操作同级'),
        ('MANAGER_PARENT', '主管-可操作上级'),
        ('MANAGER_CHILDREN', '主管-可操作下级'),
        ('ROUTE_NODE', '路由节点'),
    ]
    yes_choices = [('Y', '是'), ('N', '否')]

    permission = models.ForeignKey(RolePermission, verbose_name='权限ID', on_delete=models.DO_NOTHING, help_text='')
    module = models.CharField(verbose_name='模块名', max_length=255, blank=True, null=True, choices=module_choices, help_text='')
    feature = models.CharField(verbose_name='功能名', max_length=255, blank=True, null=True, choices=feature_choices, help_text='group: 按用户组给权限, route: 按路由给权限, point: 按交互点给权限, ..., category: 类别权限')
    permission_value = models.CharField(verbose_name='权限值', max_length=255, blank=True, null=True, help_text='权限标识值，一个permission_id可以对应多个value，一个value有多个flag，多值和标志组成一组权限。多值用分号隔开，值在不功能点中作用也不相同')
    flag = models.CharField(verbose_name='标识', max_length=255, blank=True, null=True, choices=flag_choices, help_text='标识为宏名，需要多语言翻译')
    type = models.CharField(verbose_name='类型', max_length=255, blank=True, null=True, help_text='暂不使用')
    relate_key = models.CharField(verbose_name='权限内容关联键', max_length=255, blank=True, null=True, help_text='')
    relate_value = models.CharField(verbose_name='权限内容关联值', max_length=255, blank=True, null=True, help_text='')
    config = models.CharField(verbose_name='权限更多配置', max_length=255, blank=True, null=True, help_text='权限更多配置，常用于前端路由')
    is_enable = models.CharField(verbose_name='是否启用权限', max_length=1, blank=True, null=True, choices=yes_choices, help_text='')
    is_system = models.CharField(verbose_name='是否系统权限', max_length=1, blank=True, null=True, choices=yes_choices, help_text='是否系统权限，系统权限不可以删除，默认SUPER_ADMINISTRATOR的所有value都是系统权限。')
    is_ban = models.CharField(verbose_name='全部禁止', max_length=1, blank=True, null=True, choices=yes_choices, help_text='是否全部禁用该权限，Y禁用，N允许，默认N。使用减法原则，约定无权限值则视为允许。')
    ban_view = models.CharField(verbose_name='禁止查看', max_length=1, blank=True, null=True, choices=yes_choices, help_text='')
    ban_edit = models.CharField(verbose_name='禁止编辑', max_length=1, blank=True, null=True, choices=yes_choices, help_text='')
    ban_add = models.CharField(verbose_name='禁止添加', max_length=1, blank=True, null=True, choices=yes_choices, help_text='')
    ban_delete = models.CharField(verbose_name='禁止删除', max_length=1, blank=True, null=True, choices=yes_choices, help_text='')
    description = models.CharField(verbose_name='权限值描述', max_length=255, blank=True, null=True, help_text='权限值描述')

    class Meta:
        db_table = 'role_permission_value'
        verbose_name_plural = "06. 角色 - 权限组值表"
        ordering = ['id']

    def __str__(self):
        return f"{self.permission_value}"

    def short_relate_value(self):
        if len(str(self.relate_value)) > 30:
            return '{}...'.format(str(self.relate_value)[0:30])
        return self.relate_value
    short_relate_value.short_description = '权限内容关联值'

    def short_config(self):
        if len(str(self.config)) > 30:
            return '{}...'.format(str(self.config)[0:30])
        return self.config
    short_config.short_description = '权限更多配置'


class RoleUserGroup(models.Model):
    """ 3、Role_RoleUserGroup 用户分组表 """
    id = models.AutoField(verbose_name='ID', primary_key=True, help_text='')
    group = models.CharField(verbose_name='用户组', max_length=32, blank=True, null=True, help_text='')
    group_name = models.CharField(verbose_name='用户组名', max_length=32, blank=True, null=True, help_text='')
    # parent_group_id = models.ForeignKey(verbose_name='父组ID', to="self", db_column='parent_group_id', unique=False, blank=True, null=True, on_delete=models.DO_NOTHING, help_text='父级组ID')
    parent_group_id = models.IntegerField(verbose_name='父组ID', blank=True, null=True, help_text='')
    description = models.CharField(verbose_name='描述', max_length=32, blank=True, null=True, help_text='')

    class Meta:
        db_table = 'role_user_group'
        verbose_name_plural = "03. 角色 - 用户分组表"

    def __str__(self):
        return f"{self.group}"


class Role(models.Model):
    """ 1、Role_Role 主表 [NF1]"""
    id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, help_text='')
    role = models.CharField(verbose_name='角色', max_length=32, blank=True, null=True, help_text='')
    role_name = models.CharField(verbose_name='角色名称', max_length=32, blank=True, null=True, help_text='')
    parent_role_id = models.IntegerField(verbose_name='父级角色ID', blank=True, null=True, help_text='')
    permission = models.ForeignKey(RolePermission, verbose_name='权限ID', max_length=32, blank=True, null=True, help_text='', on_delete=models.DO_NOTHING, )
    user_group = models.ForeignKey(RoleUserGroup, verbose_name='分组ID', max_length=32, blank=True, null=True, help_text='', on_delete=models.DO_NOTHING, )
    description = models.CharField(verbose_name='描述', max_length=32, blank=True, null=True, help_text='')

    class Meta:
        db_table = 'role_role'
        verbose_name_plural = "01. 角色 - 角色列表"

    def __str__(self):
        return f"{self.role_name}"


class UserToGroup(models.Model):
    """  4、Role_UserToGroup 多对多用户分组表[N-N]** """
    id = models.IntegerField(verbose_name='ID', primary_key=True, auto_created=True, help_text='')
    user_id = models.IntegerField(verbose_name='用户ID', blank=True, null=True, help_text='')
    user_group = models.ForeignKey(RoleUserGroup, verbose_name='分组ID', blank=True, null=True, on_delete=models.DO_NOTHING, help_text='')

    class Meta:
        db_table = 'role_user_to_group'
        verbose_name_plural = "04. 角色 - 多对多用户分组表"

    def __str__(self):
        return f"{self.user_group}"


class UserToRole(models.Model):
    """  2、Role_UserToRole 多对多用户角色表[N-N] """
    id = models.IntegerField(verbose_name='ID', primary_key=True, auto_created=True, help_text='')
    user_id = models.IntegerField(verbose_name='用户ID', blank=True, null=True, help_text='')
    role = models.ForeignKey(Role, verbose_name='角色ID', blank=True, null=True, on_delete=models.DO_NOTHING, help_text='')

    class Meta:
        db_table = 'role_user_to_role'
        verbose_name_plural = "02. 角色 - 多对多用户角色表"

    def __str__(self):
        return f"{self.role}"

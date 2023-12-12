from django.db import models
from common.db import BaseModel
from django.contrib.auth.models import AbstractUser

class User(AbstractUser, BaseModel):
    """
    用户表
    """

    mobile = models.CharField(verbose_name='手机号', max_length=11, default='')
    avatars = models.ImageField(verbose_name='头像', default='', blank=True, null=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户表'


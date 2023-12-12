'''
白定义用户登录的认证类，实现多字段登录
'''

from django.contrib.auth.backends import ModelBackend
from users.models import User
from django.db.models import Q
from rest_framework import serializers


class MyBackend(ModelBackend):
    '''
    自定义用户认证类
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        重写authenticate方法，实现多字段登录
        '''
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
        except:
            raise serializers.ValidationError('用户名不存在')
        # 验证密码
        if user.check_password(password):
            return user
        else:
            raise serializers.ValidationError('密码错误')
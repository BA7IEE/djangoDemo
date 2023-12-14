from django.contrib.auth.backends import ModelBackend
from users.models import User
from django.db.models import Q
from rest_framework import serializers

class MyBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
        except User.DoesNotExist:
            raise serializers.ValidationError('用户名不存在')

        if user.check_password(password):
            return user
        else:
            raise serializers.ValidationError('密码错误')

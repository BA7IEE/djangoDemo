from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','mobile', 'email', 'is_staff', 'is_active', 'is_superuser', 'last_name', 'avatars']

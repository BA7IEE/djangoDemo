import os

from django.http import FileResponse
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from djangoDemo.settings import MEDIA_ROOT
from users.models import User
from .permissions import UserPermission
from .serializers import UserSerializer


class RegisterView(APIView):
    """
    自定义注册视图
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        mobile = request.data.get('mobile')
        email = request.data.get('email')
        password_confirmation = request.data.get('password_confirmation')

        if not all([username, password, email, password_confirmation]):
            return Response({'message': '缺少参数'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'message': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'message': '邮箱已存在'}, status=status.HTTP_400_BAD_REQUEST)
        if password != password_confirmation:
            return Response({'message': '两次密码不一致'}, status=status.HTTP_400_BAD_REQUEST)

        obj = User.objects.create_user(username=username, password=password, email=email, mobile=mobile)
        res = {
            'id': obj.id,
            'username': obj.username,
            'mobile': obj.mobile,
            'email': obj.email
        }
        return Response(res, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    """
    自定义登录视图
    """
    def post(self, request, *args, **kwargs):
        """
        Generate a new JWT token for the user.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        # 自定义登录成功之后返回的结果
        result = serializer.validated_data
        result['id'] = serializer.user.id
        result['username'] = serializer.user.username
        result['mobile'] = serializer.user.mobile
        result['email'] = serializer.user.email
        result['token'] = result.pop('access')
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserView(GenericViewSet, mixins.RetrieveModelMixin):
    """
    用户视图
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserPermission]

    def upload_avatar(self, request, *args, **kwargs):
        """
        上传头像
        """
        avatars = request.data.get('avatars')
        if not avatars:
            return Response({'message': '上传失败，不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if avatars.size > 1024 * 1024:
            return Response({'message': '上传失败，不能大于1024*1024'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        user = self.get_object()
        serializer = self.get_serializer(user, data={'avatars': avatars}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'url': serializer.data['avatars']}, status=status.HTTP_201_CREATED)

class FileView(APIView):
    def get(self, request, name): # 获取文件
        path = MEDIA_ROOT / name # 绝对路径
        if os.path.isfile(path): # 判断文件是否存在
            return FileResponse(open(path, 'rb'), as_attachment=True) # 下载文件
        return Response({'message': '文件不存在'}, status=status.HTTP_404_NOT_FOUND) # 404
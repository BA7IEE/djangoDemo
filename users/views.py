import os
from pathlib import Path
from django.http import FileResponse
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from djangoDemo.settings import MEDIA_ROOT
from users.models import User
from .permissions import UserPermission
from .serializers import UserSerializer

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except AuthenticationFailed as e:
            raise InvalidToken(e.args[0])

        result = serializer.validated_data
        result.update({
            'id': serializer.user.id,
            'username': serializer.user.username,
            'mobile': serializer.user.mobile,
            'email': serializer.user.email,
        })

        return Response(result, status=status.HTTP_200_OK)

class UserView(GenericViewSet, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserPermission]

    def upload_avatar(self, request, *args, **kwargs):
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
    def get(self, request, name):
        path = Path(MEDIA_ROOT) / name
        if path.is_file():
            return FileResponse(open(path, 'rb'), as_attachment=True)
        return Response({'message': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)

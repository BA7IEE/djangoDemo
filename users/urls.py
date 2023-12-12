from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('token/verify/', TokenVerifyView.as_view()),
    path('users/<int:pk>/', views.UserView.as_view({'get': 'retrieve'})),
    path('<int:pk>/avatar/upload/', views.UserView.as_view({'post': 'upload_avatar'}))
]

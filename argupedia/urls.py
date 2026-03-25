from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from backend.views import RegisterView, MeView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth — matches what AuthContext.js expects
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Register + current user
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/me/',       MeView.as_view(),       name='me'),
]
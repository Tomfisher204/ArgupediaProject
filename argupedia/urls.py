from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from backend.views.auth_views     import RegisterView, MeView
from backend.views.argument_views import ThemeListView, ThemeArgumentsView, ArgumentDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Auth
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/me/',       MeView.as_view(),       name='me'),

    # Themes + arguments
    path('api/themes/',                          ThemeListView.as_view(),      name='theme_list'),
    path('api/themes/<int:theme_id>/arguments/', ThemeArgumentsView.as_view(), name='theme_arguments'),
    path('api/arguments/<int:argument_id>/',     ArgumentDetailView.as_view(), name='argument_detail'),
]
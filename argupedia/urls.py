from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from backend.views import SchemeListView, CreateArgumentView, ThemeRequestView, ThemeListView, ThemeArgumentsView, ArgumentDetailView, RegisterView, MeView, UserArgumentsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/me/', MeView.as_view(), name='me'),
    path('api/themes/', ThemeListView.as_view(), name='theme_list'),
    path('api/themes/<int:theme_id>/arguments/', ThemeArgumentsView.as_view(), name='theme_arguments'),
    path('api/arguments/<int:argument_id>/', ArgumentDetailView.as_view(), name='argument_detail'),
    path('api/schemes/', SchemeListView.as_view(), name='scheme_list'),
    path('api/arguments/create/', CreateArgumentView.as_view(), name='argument_create'),
    path('api/theme-requests/', ThemeRequestView.as_view(), name='theme_request'),
    path('api/user/arguments/', UserArgumentsView.as_view(), name='user_arguments'),
]
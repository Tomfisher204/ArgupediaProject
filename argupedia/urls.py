from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from backend.views import SchemeListView, CreateArgumentView, ThemeRequestView, ThemeListView, ThemeArgumentsView, ArgumentDetailView, RegisterView, MeView, UserArgumentsView, AdminStatsView, AdminThemeRequestsView, AdminThemeView, ReportArgumentView, AdminReportedArgumentsView, AdminSchemesView, AdminCriticalQuestionsView

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
    path('api/arguments/<int:argument_id>/report/', ReportArgumentView.as_view(), name='report_argument'),
    path('api/user/arguments/', UserArgumentsView.as_view(), name='user_arguments'),
    path('api/admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('api/admin/theme-requests/', AdminThemeRequestsView.as_view(), name='admin_theme_requests'),
    path('api/admin/reported-arguments/', AdminReportedArgumentsView.as_view(), name='admin_reported_arguments'),
    path('api/admin/theme/<int:theme_id>/', AdminThemeView.as_view(), name='admin_theme'),
    path('api/admin/schemes/', AdminSchemesView.as_view(), name='admin_schemes'),
    path('api/admin/schemes/<int:scheme_id>/', AdminSchemesView.as_view(), name='admin_scheme_detail'),
    path('api/admin/critical-questions/', AdminCriticalQuestionsView.as_view(), name='admin_critical_questions'),
    path('api/admin/critical-questions/<int:cq_id>/', AdminCriticalQuestionsView.as_view(), name='admin_critical_question_detail'),
]
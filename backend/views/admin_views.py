from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from backend.models import User, Argument, ArgumentTheme, ThemeRequest


class IsAdminPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_admin


class AdminStatsView(APIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        total_users = User.objects.count()
        total_arguments = Argument.objects.count()
        total_themes = ArgumentTheme.objects.count()
        pending_theme_requests = ThemeRequest.objects.filter(status='pending').count()

        return Response({
            'total_users': total_users,
            'total_arguments': total_arguments,
            'total_themes': total_themes,
            'pending_theme_requests': pending_theme_requests,
        })


class AdminThemeRequestsView(APIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        theme_requests = ThemeRequest.objects.select_related('requested_by').order_by('-date_created')
        data = []
        for tr in theme_requests:
            data.append({
                'id': tr.id,
                'title': tr.title,
                'description': tr.description,
                'reason': tr.reason,
                'status': tr.status,
                'date_created': tr.date_created,
                'requested_by': {
                    'id': tr.requested_by.id,
                    'username': tr.requested_by.username,
                }
            })
        return Response(data)

    def post(self, request):
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        if not action or not request_id:
            return Response({'error': 'action and request_id required'}, status=400)

        tr = ThemeRequest.objects.get(id=request_id)
        if action == 'approve':
            # Create new theme
            theme = ArgumentTheme.objects.create(
                title=tr.title,
                description=tr.description,
                creator=tr.requested_by
            )
            tr.status = 'approved'
        elif action == 'reject':
            tr.status = 'rejected'
        else:
            return Response({'error': 'invalid action'}, status=400)

        from django.utils import timezone
        tr.reviewed_at = timezone.now()
        tr.save()
        return Response({'status': 'success'})
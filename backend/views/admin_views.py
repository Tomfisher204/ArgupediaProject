import re
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from backend.models import User, Argument, ArgumentTheme, ThemeRequest, ArgumentScheme, CriticalQuestion, SchemeField
from .permissions import IsAdminPermission

class AdminStatsView(APIView):
    """Returns overall platform statistics for admin dashboard."""
    permission_classes = [IsAdminPermission]
    def get(self, request):
        return Response({
            'total_users': User.objects.count(),
            'total_arguments': Argument.objects.count(),
            'total_themes': ArgumentTheme.objects.count(),
            'pending_theme_requests': ThemeRequest.objects.filter(status='pending').count(),
        })

class AdminThemeView(APIView):
    """Deletes a theme."""
    permission_classes = [IsAdminPermission]
    def delete(self, request, theme_id):
        theme = get_object_or_404(ArgumentTheme, id=theme_id)
        try:
            theme.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({'error': 'Cannot delete theme'}, status=status.HTTP_400_BAD_REQUEST)

class AdminThemeRequestsView(APIView):
    """Returns pending theme requests and allows approving/rejecting them."""
    permission_classes = [IsAdminPermission]
    
    def get(self, request):
        theme_requests = (ThemeRequest.objects.filter(status='pending').select_related('requested_by').order_by('-date_created'))
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(theme_requests, request)
        data = [
            {
                'id': tr.id,
                'title': tr.title,
                'description': tr.description,
                'reason': tr.reason,
                'status': tr.status,
                'date_created': tr.date_created,
                'requested_by': {'id': tr.requested_by.id, 'username': tr.requested_by.username},
            }
            for tr in result_page
        ]
        return paginator.get_paginated_response(data)
    
    def post(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')
        if not request_id or not action:
            return Response({'error': 'request_id and action are required'}, status=status.HTTP_400_BAD_REQUEST)
        theme_request = get_object_or_404(ThemeRequest, id=request_id)
        if action == 'approve':
            ArgumentTheme.objects.create(
                title=theme_request.title,
                description=theme_request.description,
                creator=theme_request.requested_by,
            )
            theme_request.status = 'approved'
        elif action == 'reject':
            theme_request.status = 'rejected'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        theme_request.reviewed_at = timezone.now()
        theme_request.save()
        return Response({'status': 'success'})

class AdminReportedArgumentsView(APIView):
    """Returns reported arguments for admin review."""
    permission_classes = [IsAdminPermission]

    def get(self, request):
        arguments = (Argument.objects
            .filter(reported_by__isnull=False)
            .distinct()
            .annotate(report_count=Count('reported_by'))
            .order_by('-report_count', '-date_created')
            .select_related('author', 'theme', 'scheme')
            .prefetch_related('field_values__scheme_field')
        )
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(arguments, request)
        data = [
            {
                'id': arg.id,
                'theme': arg.theme.title,
                'scheme_name': arg.scheme.name,
                'scheme_template': arg.scheme.template,
                'author': arg.author.username,
                'report_count': arg.report_count,
                'date_created': arg.date_created,
                'field_values': [
                    {'field_name': fv.scheme_field.name, 'value': fv.value}
                    for fv in arg.field_values.all()
                ],
            }
            for arg in result_page
        ]
        return paginator.get_paginated_response(data)

class AdminSchemesView(APIView):
    """This view allows admins to manage argument schemes, including creating new schemes and deleting existing ones."""
    permission_classes = [IsAdminPermission]

    def get(self, request):
        schemes = (ArgumentScheme.objects.prefetch_related('critical_questions').order_by('name'))
        data = [
            {
                'id': scheme.id,
                'name': scheme.name,
                'description': scheme.description,
                'template': scheme.template,
                'critical_questions': [
                    {'id': cq.id, 'question': cq.question}
                    for cq in scheme.critical_questions.all()
                ],
            }
            for scheme in schemes
        ]
        return Response(data)

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')
        template = request.data.get('template')
        if not name or not template:
            return Response(
                {'error': 'name and template are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        scheme = ArgumentScheme.objects.create(
            name=name,
            description=description,
            template=template,
            created_by=request.user,
        )
        field_names = re.findall(r'\*\*(.*?)\*\*', template)
        for order, field_name in enumerate(field_names):
            SchemeField.objects.create(
                scheme=scheme,
                name=field_name.strip(),
                order=order,
            )
        return Response(
            {
                'id': scheme.id,
                'name': scheme.name,
                'description': scheme.description,
                'template': scheme.template,
                'fields': [
                    {'id': f.id, 'name': f.name}
                    for f in scheme.fields.all()
                ],
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, scheme_id=None):
        if not scheme_id:
            return Response({'error': 'scheme_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        scheme = get_object_or_404(ArgumentScheme, id=scheme_id)
        scheme.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminCriticalQuestionsView(APIView):
    """This view allows admins to manage critical questions for argument schemes, including adding new questions and deleting existing ones."""
    permission_classes = [IsAdminPermission]
    
    def post(self, request):
        question = request.data.get('question')
        scheme_id = request.data.get('scheme_id')
        two_way = request.data.get('two_way', False)
        if not question or not scheme_id:
            return Response({'error': 'question and scheme_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        scheme = get_object_or_404(ArgumentScheme, id=scheme_id)
        cq = CriticalQuestion.objects.create(
            scheme=scheme,
            question=question,
            two_way=bool(two_way),
        )
        return Response({'id': cq.id, 'question': cq.question, 'two_way': cq.two_way}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, cq_id=None):
        if not cq_id:
            return Response(
                {'error': 'cq_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cq = get_object_or_404(CriticalQuestion, id=cq_id)
        cq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
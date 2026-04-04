from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from backend.models import User, Argument, ArgumentTheme, ThemeRequest, ArgumentScheme, CriticalQuestion


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
        theme_requests = ThemeRequest.objects.filter(status='pending').select_related('requested_by').order_by('-date_created')
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(theme_requests, request)
        data = []
        for tr in result_page:
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
        return paginator.get_paginated_response(data)

    def post(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')
        
        if not request_id or not action:
            return Response({'error': 'request_id and action are required'}, status=400)
        
        try:
            theme_request = ThemeRequest.objects.get(id=request_id)
        except ThemeRequest.DoesNotExist:
            return Response({'error': 'Theme request not found'}, status=404)
        
        if action == 'approve':
            theme_request.status = 'approved'
            # TODO: Create the actual theme if needed
        elif action == 'reject':
            theme_request.status = 'rejected'
        else:
            return Response({'error': 'Invalid action'}, status=400)
        
        theme_request.save()
        return Response({'status': 'success'})


class AdminReportedArgumentsView(APIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        arguments = Argument.objects.filter(reported_by__isnull=False).distinct().annotate(
            report_count=Count('reported_by')
        ).order_by('-report_count', '-date_created').select_related('author', 'theme', 'scheme').prefetch_related('field_values__scheme_field')
        
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(arguments, request)
        
        data = []
        for arg in result_page:
            data.append({
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
                ]
            })
        
        return paginator.get_paginated_response(data)

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


class AdminSchemesView(APIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        schemes = ArgumentScheme.objects.prefetch_related('critical_questions').order_by('name')
        data = []
        for scheme in schemes:
            data.append({
                'id': scheme.id,
                'name': scheme.name,
                'description': scheme.description,
                'template': scheme.template,
                'critical_questions': [
                    {'id': cq.id, 'question': cq.question}
                    for cq in scheme.critical_questions.all()
                ]
            })
        return Response(data)

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')
        template = request.data.get('template')
        
        if not name or not template:
            return Response({'error': 'name and template are required'}, status=400)
        
        scheme = ArgumentScheme.objects.create(
            name=name,
            description=description,
            template=template,
            created_by=request.user
        )
        return Response({
            'id': scheme.id,
            'name': scheme.name,
            'description': scheme.description,
            'template': scheme.template,
            'critical_questions': []
        })

    def delete(self, request, scheme_id=None):
        if not scheme_id:
            return Response({'error': 'scheme_id is required'}, status=400)
        
        try:
            scheme = ArgumentScheme.objects.get(id=scheme_id)
            scheme.delete()
            return Response({'status': 'success'})
        except ArgumentScheme.DoesNotExist:
            return Response({'error': 'Scheme not found'}, status=404)


class AdminCriticalQuestionsView(APIView):
    permission_classes = [IsAdminPermission]

    def post(self, request):
        question = request.data.get('question')
        scheme_id = request.data.get('scheme_id')
        two_way = request.data.get('two_way', False)  # NEW
        if not question or not scheme_id:
            return Response(
                {'error': 'question and scheme_id are required'},
                status=400
            )
        try:
            scheme = ArgumentScheme.objects.get(id=scheme_id)
            cq = CriticalQuestion.objects.create(
                scheme=scheme,
                question=question,
                two_way=bool(two_way)  # NEW
            )
            return Response({
                'id': cq.id,
                'question': cq.question,
                'two_way': cq.two_way   # NEW
            })
        except ArgumentScheme.DoesNotExist:
            return Response({'error': 'Scheme not found'}, status=404)

    def delete(self, request, cq_id=None):
        if not cq_id:
            return Response({'error': 'cq_id is required'}, status=400)
        try:
            cq = CriticalQuestion.objects.get(id=cq_id)
            cq.delete()
            return Response({'status': 'success'})
        except CriticalQuestion.DoesNotExist:
            return Response(
                {'error': 'Critical question not found'},
                status=404
            )
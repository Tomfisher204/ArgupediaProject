from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from backend.models import ArgumentTheme, Argument
from backend.serializers import ThemeSerializer, ArgumentSummarySerializer

class ThemeListView(APIView):
    """
    GET /api/themes/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get('q', '').strip()
        themes = ArgumentTheme.objects.all()
        if search:
            themes = themes.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        themes = themes.annotate(
            initial_argument_count=Count(
                'argument',
                filter=Q(argument__parent_links__isnull=True),
            )
        )
        sort = request.GET.get('sort', '').strip().lower()
        sort_map = {
            'arg_size_asc':  ('initial_argument_count', 'title'),
            'arg_size_desc': ('-initial_argument_count', 'title'),
            'alpha_asc':     ('title',),
            'alpha_desc':    ('-title',),
            'date_asc':      ('date_created',),
            'date_desc':     ('-date_created',),
        }
        themes = themes.order_by(*sort_map.get(sort, ('title',)))
        paginator = PageNumberPagination()
        paginator.page_size = 16
        result_page = paginator.paginate_queryset(themes, request)
        serializer = ThemeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ThemeArgumentsView(APIView):
    """
    GET /api/themes/<theme_id>/arguments/
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, theme_id):
        theme = get_object_or_404(ArgumentTheme, id=theme_id)

        initial_arguments = (
            Argument.objects
            .filter(theme=theme)
            .exclude(parent_links__isnull=False)
            .select_related('author', 'theme', 'scheme')
            .prefetch_related('field_values__scheme_field')
            .distinct()
        )
        serializer = ArgumentSummarySerializer(initial_arguments, many=True)
        return Response({
            'theme': ThemeSerializer(theme).data,
            'arguments': serializer.data,
        })
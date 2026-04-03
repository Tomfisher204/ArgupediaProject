from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from backend.models import ArgumentTheme, Argument
from backend.serializers import ThemeSerializer, ArgumentSummarySerializer, ArgumentDetailSerializer


class IsAdminPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_admin

class ThemeListView(APIView):
    """
    GET /api/themes/
    Returns all argument themes with their argument counts.
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
            initial_argument_count=Count('argument', filter=Q(argument__parent_links__isnull=True))
        )

        sort = request.GET.get('sort', '').strip().lower()
        if sort == 'arg_size_asc':
            themes = themes.order_by('initial_argument_count', 'title')
        elif sort == 'arg_size_desc':
            themes = themes.order_by('-initial_argument_count', 'title')
        elif sort == 'alpha_asc':
            themes = themes.order_by('title')
        elif sort == 'alpha_desc':
            themes = themes.order_by('-title')
        elif sort == 'date_asc':
            themes = themes.order_by('date_created')
        elif sort == 'date_desc':
            themes = themes.order_by('-date_created')
        else:
            themes = themes.order_by('title')

        paginator = PageNumberPagination()
        paginator.page_size = 16
        result_page = paginator.paginate_queryset(themes, request)
        serializer = ThemeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ThemeArgumentsView(APIView):
    """
    GET /api/themes/<theme_id>/arguments/
    Returns all INITIAL arguments for a theme.
    An initial argument is one with no parent links (nothing is attacking/supporting it).
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


class ArgumentDetailView(APIView):
    """
    GET /api/arguments/<argument_id>/
    Returns full argument detail including attackers and supporters as child cards.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, argument_id):
        argument = get_object_or_404(
            Argument.objects
            .select_related('author', 'theme', 'scheme')
            .prefetch_related(
                'field_values__scheme_field',
                'child_links__child_argument__author',
                'child_links__child_argument__theme',
                'child_links__child_argument__scheme',
                'child_links__child_argument__field_values__scheme_field',
                'child_links__critical_question',
            ),
            id=argument_id,
        )

        serializer = ArgumentDetailSerializer(argument)
        return Response(serializer.data)

    def delete(self, request, argument_id):
        # Only admins can delete arguments
        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        argument = get_object_or_404(Argument, id=argument_id)
        argument.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminThemeView(APIView):
    permission_classes = [IsAdminPermission]

    def delete(self, request, theme_id):
        try:
            theme = get_object_or_404(ArgumentTheme, id=theme_id)
            theme.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'error': 'Cannot delete theme'}, status=400)


class UserArgumentsView(APIView):
    """
    GET /api/user/arguments/
    Returns all arguments created by the current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        arguments = (
            Argument.objects
            .filter(author=request.user)
            .select_related('author', 'theme', 'scheme')
            .prefetch_related('field_values__scheme_field')
            .order_by('-date_created')
        )
        paginator = PageNumberPagination()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(arguments, request)
        serializer = ArgumentSummarySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
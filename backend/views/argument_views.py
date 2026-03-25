from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from backend.models import ArgumentTheme, Argument
from backend.serializers.argument_serializer import (
    ThemeSerializer,
    ArgumentSummarySerializer,
    ArgumentDetailSerializer,
)


class ThemeListView(APIView):
    """
    GET /api/themes/
    Returns all argument themes with their argument counts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        themes = ArgumentTheme.objects.all().order_by('title')
        serializer = ThemeSerializer(themes, many=True)
        return Response(serializer.data)


class ThemeArgumentsView(APIView):
    """
    GET /api/themes/<theme_id>/arguments/
    Returns all INITIAL arguments for a theme.
    An initial argument is one with no parent links (nothing is attacking/supporting it).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, theme_id):
        theme = get_object_or_404(ArgumentTheme, id=theme_id)

        # Initial arguments have no ArgumentLink pointing to them as child_argument
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
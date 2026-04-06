from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from backend.models import Argument
from backend.serializers import ArgumentSummarySerializer, ArgumentDetailSerializer, CreateArgumentSerializer
from backend.utils import evaluate_and_propagate

class ArgumentDetailView(APIView):
    """
    GET /api/arguments/<argument_id>/
    DELETE /api/arguments/<argument_id>/
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
        if not request.user.is_admin:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN,
            )
        argument = get_object_or_404(Argument, id=argument_id)
        parents = list(
            Argument.objects
            .filter(child_links__child_argument=argument)
            .distinct()
        )
        argument.delete()
        for parent in parents:
            evaluate_and_propagate(parent)

        return Response(status=status.HTTP_204_NO_CONTENT)

class CreateArgumentView(APIView):
    """
    POST /api/arguments/
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = CreateArgumentSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        argument = serializer.save()
        parents = list(
            Argument.objects
            .filter(child_links__child_argument=argument)
            .distinct()
        )
        for parent in parents:
            evaluate_and_propagate(parent)
        return Response({'id': argument.id}, status=status.HTTP_201_CREATED)

class UserArgumentsView(APIView):
    """
    GET /api/user/arguments/
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

class ReportArgumentView(APIView):
    """
    POST /api/arguments/<argument_id>/report/
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, argument_id):
        argument = get_object_or_404(Argument, id=argument_id)
        if argument.reported_by.filter(id=request.user.id).exists():
            argument.reported_by.remove(request.user)
            reported = False
        else:
            argument.reported_by.add(request.user)
            reported = True
        return Response({
            'reported': reported,
            'report_count': argument.reported_by.count(),
        })
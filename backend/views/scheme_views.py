from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.models import ArgumentScheme
from backend.serializers.scheme_serializer import ArgumentSchemeSerializer


class SchemeListView(APIView):
    """Gets a list of all argument schemes, including their fields and critical questions."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        schemes = (
            ArgumentScheme.objects
            .prefetch_related('fields', 'critical_questions')
            .order_by('name')
        )
        return Response(ArgumentSchemeSerializer(schemes, many=True).data)
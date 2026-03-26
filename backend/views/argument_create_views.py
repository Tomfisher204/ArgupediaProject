from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.serializers import CreateArgumentSerializer


class CreateArgumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateArgumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            argument = serializer.save()
            return Response({'id': argument.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

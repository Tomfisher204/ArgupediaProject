from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.serializers import ThemeRequestSerializer


class ThemeRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ThemeRequestSerializer(data=request.data, context={'request': request})
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import serializers
from backend.models import ThemeRequest

class ThemeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeRequest
        fields = ('id', 'requested_by', 'title', 'description', 'reason', 'status', 'date_created', 'reviewed_at')

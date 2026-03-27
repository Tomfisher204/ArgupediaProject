from rest_framework import serializers
from backend.models import ThemeRequest

class ThemeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeRequest
        fields = ('id', 'requested_by', 'title', 'description', 'reason', 'status', 'date_created', 'reviewed_at')
        read_only_fields = ('requested_by', 'status', 'date_created', 'reviewed_at')

    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)

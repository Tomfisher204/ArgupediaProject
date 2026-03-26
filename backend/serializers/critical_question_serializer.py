from rest_framework import serializers
from backend.models import CriticalQuestion

class CriticalQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CriticalQuestion
        fields = ('id', 'scheme', 'question', 'two_way', 'date_created')

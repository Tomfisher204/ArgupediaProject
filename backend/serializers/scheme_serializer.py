from rest_framework import serializers
from backend.models import ArgumentScheme, SchemeField
from backend.serializers.critical_question_serializer import CriticalQuestionSerializer

class SchemeFieldSerializer(serializers.ModelSerializer):
    """Serializes one field in a scheme."""
    class Meta:
        model = SchemeField
        fields = ('id', 'scheme', 'name', 'order')

class ArgumentSchemeSerializer(serializers.ModelSerializer):
    """Serializes an argument scheme."""
    fields = SchemeFieldSerializer(many=True, read_only=True)
    critical_questions = serializers.SerializerMethodField()
    class Meta:
        model = ArgumentScheme
        fields = ('id', 'name', 'description', 'template', 'created_by', 'date_created', 'fields', 'critical_questions')

    def get_critical_questions(self, obj):
        qs = obj.critical_questions.all()
        return CriticalQuestionSerializer(qs, many=True).data


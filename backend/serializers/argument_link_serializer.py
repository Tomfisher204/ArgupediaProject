from rest_framework import serializers
from backend.models import ArgumentLink

class ArgumentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArgumentLink
        fields = ('id', 'parent_argument', 'child_argument', 'critical_question', 'attacking', 'date_created')

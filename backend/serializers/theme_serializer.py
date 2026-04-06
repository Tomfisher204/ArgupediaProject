from rest_framework import serializers
from backend.models import ArgumentTheme, Argument

class ThemeSerializer(serializers.ModelSerializer):
    argument_count = serializers.SerializerMethodField()

    class Meta:
        model = ArgumentTheme
        fields = ('id', 'title', 'description', 'date_created', 'argument_count')

    def get_argument_count(self, obj):
        return Argument.objects.filter(theme=obj).filter(root=True).count()
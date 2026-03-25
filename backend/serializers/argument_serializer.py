from rest_framework import serializers
from backend.models import ArgumentTheme, Argument, ArgumentFieldValue, ArgumentLink


class ThemeSerializer(serializers.ModelSerializer):
    argument_count = serializers.SerializerMethodField()

    class Meta:
        model = ArgumentTheme
        fields = ('id', 'title', 'description', 'date_created', 'argument_count')

    def get_argument_count(self, obj):
        # Count only initial arguments (those with no parent links)
        return Argument.objects.filter(theme=obj).exclude(parent_links__isnull=False).count()

class FieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='scheme_field.name', read_only=True)

    class Meta:
        model = ArgumentFieldValue
        fields = ('field_name', 'value')


class ArgumentSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer used for cards (list views + child cards)."""
    author      = serializers.CharField(source='author.username', read_only=True)
    theme       = serializers.CharField(source='theme.title',     read_only=True)
    scheme_name = serializers.CharField(source='scheme.name',     read_only=True)
    field_values = FieldValueSerializer(many=True, read_only=True)
    child_count = serializers.SerializerMethodField()

    class Meta:
        model = Argument
        fields = (
            'id', 'author', 'theme', 'scheme_name',
            'field_values', 'date_created',
            'child_count',
        )

    def get_child_count(self, obj):
        return obj.child_links.count()


class ChildArgumentSerializer(serializers.ModelSerializer):
    """Serializes a child argument card — includes the link's attacking flag."""
    argument    = ArgumentSummarySerializer(source='child_argument', read_only=True)
    attacking   = serializers.BooleanField(read_only=True)
    question    = serializers.CharField(source='critical_question.question', read_only=True)

    class Meta:
        model = ArgumentLink
        fields = ('id', 'attacking', 'question', 'argument')


class ArgumentDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer — includes field values and split children."""
    author       = serializers.CharField(source='author.username',  read_only=True)
    theme        = serializers.CharField(source='theme.title',      read_only=True)
    theme_id     = serializers.IntegerField(source='theme.id',      read_only=True)
    scheme_name  = serializers.CharField(source='scheme.name',      read_only=True)
    field_values = FieldValueSerializer(many=True, read_only=True)
    attackers    = serializers.SerializerMethodField()
    supporters   = serializers.SerializerMethodField()

    class Meta:
        model = Argument
        fields = (
            'id', 'author', 'theme', 'theme_id', 'scheme_name',
            'field_values', 'date_created',
            'attackers', 'supporters',
        )

    def get_attackers(self, obj):
        links = obj.child_links.filter(attacking=True).select_related(
            'child_argument', 'critical_question',
            'child_argument__author', 'child_argument__theme', 'child_argument__scheme'
        )
        return ChildArgumentSerializer(links, many=True).data

    def get_supporters(self, obj):
        links = obj.child_links.filter(attacking=False).select_related(
            'child_argument', 'critical_question',
            'child_argument__author', 'child_argument__theme', 'child_argument__scheme'
        )
        return ChildArgumentSerializer(links, many=True).data
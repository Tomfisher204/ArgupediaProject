from rest_framework import serializers
from backend.models import Argument, ArgumentFieldValue, ArgumentLink, SchemeField

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

class ArgumentFieldValueInputSerializer(serializers.Serializer):
    scheme_field_id = serializers.IntegerField()
    value           = serializers.CharField()

class CreateArgumentSerializer(serializers.Serializer):
    """
    Creates an Argument with its field values and optionally an ArgumentLink.
    For initial arguments: omit parent_argument_id and critical_question_id.
    For responses: provide both.
    """
    scheme_id            = serializers.IntegerField()
    theme_id             = serializers.IntegerField()
    field_values         = ArgumentFieldValueInputSerializer(many=True)
    parent_argument_id   = serializers.IntegerField(required=False, allow_null=True)
    critical_question_id = serializers.IntegerField(required=False, allow_null=True)
    attacking            = serializers.BooleanField(required=False, default=True)

    def validate(self, data):
        has_parent   = bool(data.get('parent_argument_id'))
        has_question = bool(data.get('critical_question_id'))

        if has_parent and not has_question:
            raise serializers.ValidationError(
                {'critical_question_id': 'A critical question is required for non-initial arguments.'}
            )
        if has_question and not has_parent:
            raise serializers.ValidationError(
                {'parent_argument_id': 'A parent argument is required when a critical question is provided.'}
            )

        scheme_id = data['scheme_id']
        field_ids = [fv['scheme_field_id'] for fv in data['field_values']]
        valid_ids = set(
            SchemeField.objects.filter(scheme_id=scheme_id).values_list('id', flat=True)
        )
        invalid = set(field_ids) - valid_ids
        if invalid:
            raise serializers.ValidationError(
                {'field_values': f'Field IDs {invalid} do not belong to the selected scheme.'}
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user

        argument = Argument.objects.create(
            author_id = user.id,
            scheme_id = validated_data['scheme_id'],
            theme_id  = validated_data['theme_id'],
        )

        ArgumentFieldValue.objects.bulk_create([
            ArgumentFieldValue(
                argument         = argument,
                scheme_field_id  = fv['scheme_field_id'],
                value            = fv['value'],
            )
            for fv in validated_data['field_values']
        ])

        parent_id   = validated_data.get('parent_argument_id')
        question_id = validated_data.get('critical_question_id')
        if parent_id and question_id:
            ArgumentLink.objects.create(
                parent_argument_id   = parent_id,
                child_argument       = argument,
                critical_question_id = question_id,
                attacking            = validated_data.get('attacking', True),
            )

        return argument
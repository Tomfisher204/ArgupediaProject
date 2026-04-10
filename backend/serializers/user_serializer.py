from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Validates and creates a new user from the signup form."""
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

class UserSerializer(serializers.ModelSerializer):
    """Serializes the current user for the /api/auth/me/ endpoint.
    This is what gets loaded into AuthContext as `user`."""

    argument_count = serializers.SerializerMethodField()
    reputation = serializers.SerializerMethodField()
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'is_admin',
            'argument_count',
            'reputation',
            'win_rate',
        )
        read_only_fields = fields

    def get_argument_count(self, obj):
        return obj.argument_set.count()

    def get_reputation(self, obj):
        prior = 0.5
        weight = 5
        objects = obj.argument_set
        total = objects.count()
        winning = objects.filter(is_winning=True).count()
        if total == 0:
            return prior * 10
        score = (winning + prior * weight) / (total + weight)
        return round(score * 10, 0)

    def get_win_rate(self, obj):
        objects = obj.argument_set
        winning = objects.filter(is_winning=True)
        win_rate = (winning.count() / objects.count()) * 100 if objects.count() > 0 else 0
        return round(win_rate, 2)
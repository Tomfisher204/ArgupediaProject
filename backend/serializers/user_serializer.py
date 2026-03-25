from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Validates and creates a new user from the signup form."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        # Use create_user so the password is hashed properly
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            # first_name and last_name are required on your model but not on the
            # signup form — defaulting to empty string; add them to the form later if needed
            first_name='',
            last_name='',
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
        # Simple reputation calculation - could be made more complex
        return obj.argument_set.count() * 10  # 10 points per argument

    def get_win_rate(self, obj):
        # For now, return None - this would need more complex logic
        # to determine "wins" based on argument links/attacks
        return None
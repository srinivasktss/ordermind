from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(allow_null=False)
    password = serializers.CharField(allow_null=False)
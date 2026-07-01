from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'assistant'])
    content = serializers.CharField()


class ChatSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)

    def validate_messages(self, messages):
        if not messages:
            raise serializers.ValidationError('messages cannot be empty.')
        if messages[-1]['role'] != 'user':
            raise serializers.ValidationError('Last message must be from the user.')
        return messages
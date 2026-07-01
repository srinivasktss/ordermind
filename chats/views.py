from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import (
    ChatSerializer
)
from agent.utils import handle_chat_request

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        req_ser = ChatSerializer(data=request.data)

        if not req_ser.is_valid():
            return JsonResponse({'detail': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = req_ser.validated_data

        # Prepare messages for the Anthropic API
        messages = validated_data['messages']

        try:
            # Call the handle_chat_request function to get the response from the Anthropic API
            response = handle_chat_request(messages, customer_id=request.user.customer.id)
        except Exception as e:
            return JsonResponse({'detail': 'Error occurred, try after some time'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({'reply': response}, status=status.HTTP_200_OK)
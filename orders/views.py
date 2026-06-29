from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'chat.html')
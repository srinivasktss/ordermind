from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

# Serializers
from .serializers import (
    LoginSerializer
)


class LoginView(APIView):

    def get(self, request):
        return render(request, 'login.html')


    def post(self, request):
        req_ser = LoginSerializer(data=request.data)

        if not req_ser.is_valid():
            return JsonResponse({'detail': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = req_ser.validated_data

        a_user = authenticate(
            request,
            username=validated_data['username'],
            password=validated_data['password'],
        )
        if not a_user:
            return JsonResponse({'detail': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, a_user)

        return JsonResponse({'detail': 'Logged in successfully'}, status=status.HTTP_200_OK)


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        logout(request)

        return redirect('login-page')
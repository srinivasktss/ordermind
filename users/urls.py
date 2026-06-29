from django.urls import path
from .views import (
    LoginView, LogoutView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login-page'),
    path('login/', LoginView.as_view(), name='do-login'),
    path('logout', LogoutView.as_view(), name='do-logout')
]
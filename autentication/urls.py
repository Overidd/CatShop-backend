from django.urls import path
from .views import (
   UserRegisterView,
   VerifyEmailView
)

urlpatterns = [
   path('register/', UserRegisterView.as_view()),
   path('verify-email/', VerifyEmailView.as_view()) 
]



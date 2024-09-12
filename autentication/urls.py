from django.urls import path
from .views import (
   UserRegisterView,
   VerifyEmailView,
   UserloginView
)

urlpatterns = [
   path('register/', UserRegisterView.as_view()),
   path('verify-email/', VerifyEmailView.as_view()),
   path('login/', UserloginView.as_view()),
]



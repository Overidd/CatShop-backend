from django.urls import path
from .views import (
   UserRegisterView,
   VerifyEmailView,
   UserloginView,
   ResendCodeView,
   RoleListView,
   RoleCreateView
)

urlpatterns = [
   path('register/', UserRegisterView.as_view()),
   path('verify-email/', VerifyEmailView.as_view()),
   path('resend-code/', ResendCodeView.as_view()),
   path('login/', UserloginView.as_view()),

   path('roles/create/', RoleCreateView.as_view()),
   path('roles/', RoleListView.as_view()),
]



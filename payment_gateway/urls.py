
from django.urls import path
from .views import (
   RegisterOrderView,
)

urlpatterns = [
   path('register/', RegisterOrderView.as_view()),
]
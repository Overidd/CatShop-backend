from django.urls import path
from .views import (
   ProductCategoryView,
   ProductView
)

urlpatterns = [
   path('categories/', ProductCategoryView.as_view()),
   path('products/', ProductView.as_view()),
]

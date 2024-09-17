from django.urls import path
from .views import (
   ProductCategoryView,
   ProductView,
   CreateProductView,
)

urlpatterns = [
   path('create/', CreateProductView.as_view()),  
   path('categories/', ProductCategoryView.as_view()),
   path('products/', ProductView.as_view()),
]

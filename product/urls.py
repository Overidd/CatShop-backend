from django.urls import path
from .views import (
   ProductCategoryView,
   # ProductView,
   CreateProductView,
   ProductListAllView,
   UpdateProductView,
   GetByIdProduct,
   IsActiveProduc,
)

urlpatterns = [
   # path('products/', ProductView.as_view()),
   path('all/', ProductListAllView.as_view()),
   path('create/', CreateProductView.as_view()),  
   path('update/<int:pk>/', UpdateProductView.as_view()),
   path('get/<int:pk>', GetByIdProduct.as_view()),
   path('isactive/<int:pk>', IsActiveProduc.as_view()),

   path('categories/', ProductCategoryView.as_view()),
]

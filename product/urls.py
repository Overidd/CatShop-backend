from django.urls import path
from .views import (
   ProductCategoryView,
   CreateProductView,
   ProductListAllView,
   UpdateProductView,
   GetByIdProduct,
   IsActiveProduc,
   VerifyQuantity,
   ProductCategoryUpdateView,
   ProductBrandView,
   ProductBrandUpdateView,
)

urlpatterns = [
   # path('products/', ProductView.as_view()),
   path('all/', ProductListAllView.as_view()),
   path('create/', CreateProductView.as_view()),  
   path('update/<int:pk>/', UpdateProductView.as_view()),
   path('get/<int:pk>', GetByIdProduct.as_view()),
   path('isactive/<int:pk>', IsActiveProduc.as_view()),
   path('verify-quantity/', VerifyQuantity.as_view()),

   path('categories/', ProductCategoryView.as_view()),
   path('categories/update/<int:pk>', ProductCategoryUpdateView.as_view()),

   path('brands/', ProductBrandView.as_view()),
   path('brands/update/<int:pk>', ProductBrandUpdateView.as_view()),
]

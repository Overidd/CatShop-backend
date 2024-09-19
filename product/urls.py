from django.urls import path
from .views import (
   CreateProductView,
   ProductListAllView,
   UpdateProductView,
   GetByIdProduct,
   IsActiveProduc,
   VerifyQuantity,
   
   ProductCategoryGelAllView,
   ProductCategoryCreate,
   ProductCategoryUpdateView,

   ProductBrandGelAllView,
   ProductBrandCreateView,
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

   path('category/get_all', ProductCategoryGelAllView.as_view()),
   path('category/create/', ProductCategoryCreate.as_view()), 
   path('category/update/<int:pk>', ProductCategoryUpdateView.as_view()),

   path('brand/', ProductBrandGelAllView.as_view()),
   path('brand/create/', ProductBrandCreateView.as_view()),
   path('brand/update/<int:pk>', ProductBrandUpdateView.as_view()),
]

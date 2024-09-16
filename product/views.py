from django.shortcuts import render
from rest_framework.generics import (
   ListCreateAPIView
)

from .models import (
   ProductModel,
   ProductCategoryModel
)

from .serializer import (
   ProductCategorySerializer,
   ProductSerializer,
)
# Create your views here.
class ProductView(ListCreateAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = ProductSerializer
   

class ProductCategoryView(ListCreateAPIView):
   queryset = ProductCategoryModel.objects.all()
   serializer_class = ProductCategorySerializer

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import (
   ProductModel,
   ProductCategoryModel,
   ProductDetailModel,
)

class ProductCategorySerializer(ModelSerializer):

   class Meta:
      model = ProductCategoryModel
      fields = '__all__'

   def to_representation(self, instance):
      representation = super().to_representation(instance)
      representation['image'] = instance.image.url
      return representation
      

class ProductSerializer(ModelSerializer): 
   class Meta:
      model = ProductModel
      fields = '__all__'

class MultiImageSerializer(serializers.Serializer):
   images = serializers.ListField(
      child=serializers.ImageField(),
      # use_url=True,
      max_length=1024*1024*5,  # 5MB
   )
class ProductDetailSerializer(ModelSerializer):
   class Meta:
      model = ProductDetailModel
      fields = '__all__'

class CreateProductSerializer(serializers.Serializer):
   name = serializers.CharField(max_length=100, required=True)
   price = serializers.FloatField(required=True)
   discount = serializers.IntegerField(required=False, default=0)
   description = serializers.CharField(required=False, allow_null=True)
   stock = serializers.IntegerField(required=True)
   category_id = serializers.IntegerField(required=True) 
   brand_id = serializers.IntegerField(required=False, allow_null=True)  

   color = serializers.CharField(max_length=100, required=False, allow_null=True)
   denifit = serializers.CharField(max_length=200, required=False, allow_null=True)
   dimension = serializers.CharField(max_length=100, required=False, allow_null=True)
   size = serializers.CharField(max_length=20, required=False, allow_null=True)
   characteristics = serializers.CharField(required=False, allow_null=True)
   extra = serializers.CharField(max_length=200, required=False, allow_null=True)

   images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
   )

   def to_representation(self, instance):
      # Llamar a la representación predeterminada
      representation = super().to_representation(instance)
      
      # Excluir el campo 'images'
      representation.pop('images', None)
      
      return representation
   
class UpdateProductSerializer(serializers.Serializer):
   name = serializers.CharField(max_length=100, required=False, allow_null=True)
   price = serializers.FloatField(required=False, allow_null=True)
   discount = serializers.IntegerField(required=False,allow_null=True ,default=0)
   description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
   stock = serializers.IntegerField(required=False, allow_null=True)
   category_id = serializers.IntegerField(required=False, allow_null=True) 
   brand_id = serializers.IntegerField(required=False, allow_null=True)

   color = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
   denifit = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
   dimension = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
   size = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
   characteristics = serializers.CharField(required=False, allow_null=True, allow_blank=True)
   extra = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)


   images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
   )

   ids_destroy_images = serializers.ListField(
      child=serializers.IntegerField(), 
      required=False,  
      allow_empty=True  # Permite que la lista esté vacía
   )

   default_image_id = serializers.IntegerField(required=False, allow_null=True) 
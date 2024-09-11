
from rest_framework.serializers import ModelSerializer
from .models import ProductCategoryModel


class ProductCategorySerializer(ModelSerializer):

   class Meta:
      model = ProductCategoryModel
      fields = '__all__'

   def to_representation(self, instance):
      representation = super().to_representation(instance)
      representation['image'] = instance.image.url
      return representation
      
      


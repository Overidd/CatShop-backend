from rest_framework import serializers

from .models import (
   OffersModel,
   StoreModel
)
class StoreSerializer(serializers.ModelSerializer):
   class Meta:
      model = StoreModel
      fields = '__all__'

class OffersSerializer(serializers.ModelSerializer):
   class Meta:
      model = OffersModel
      fields = '__all__'
    






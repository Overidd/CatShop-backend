from rest_framework import serializers
from purchases.models import (
   OrderDetailModel,
   OrderIdentificationModel,
   OrderDeliveryModel,
   OrderStoreModel,
   OrderPaymentModel,
)

# Serializador para "isuser" (opcional)
class IsUserSerializer(serializers.Serializer):
   isuser = serializers.BooleanField(required=False)
   token = serializers.CharField(required=False)
   id_user = serializers.IntegerField(required=False)
   email = serializers.EmailField(required=False)

# Serializador para "order"

   

# Serializador para "order_identification"
class OrderIdentificationSerializer(serializers.ModelSerializer):
   class Meta:
      model = OrderIdentificationModel
      
      fields = [
         'email',
         'name',
         'last_name',
         'document_number',
         'phone',
         'ruc'
      ]
   

# Serializador para "order_store" (opcional)
class OrderStoreSerializer(serializers.ModelSerializer):
   class Meta:
      model = OrderStoreModel
      fields = ['store_name']

# Serializador para "order_delivery" (opcional)
class OrderDeliverySerializer(serializers.ModelSerializer):
   class Meta:
      model = OrderDeliveryModel
      fields = [
         'department',
         'province',
         'district',
         'address',
         'street',
         'street_number',
         'reference'
      ]

# Serializador para "order_payment"
class OrderPaymentSerializer(serializers.ModelSerializer):
   class Meta:
      model = OrderPaymentModel
      fields = [
         'amount',
         'payment_method',
      ]

# Serializador para "order_details"
class OrderDetailSerializer(serializers.ModelSerializer):
   product_id = serializers.IntegerField()  # Solo recibirá el ID del producto

   class Meta:
      model = OrderDetailModel
      fields = [
         'quantity',
         'price_unit',
         'product_id',
      ]

# Serializador principal
class RegisterOrderSerializer(serializers.Serializer):
    opciones_entrega = serializers.CharField(max_length=50)
    isuser = IsUserSerializer(required=False)
    order_identification = OrderIdentificationSerializer()
    order_store = OrderStoreSerializer(required=False)  # Opcional
    order_delivery = OrderDeliverySerializer(required=False)  # Opcional
   #  order_payment = OrderPaymentSerializer()
    order_details = OrderDetailSerializer(many=True)

    def validate(self, data):
        """
        Validar que uno de 'order_store' o 'order_delivery' esté presente.
        """
        if not data.get('order_store') and not data.get('order_delivery'):
            raise serializers.ValidationError("Debe proporcionar 'order_store' o 'order_delivery'.")
        return data


class ProcessPaymentSerializer(serializers.Serializer):
   token_id = serializers.CharField(max_length=100)
   code_order = serializers.CharField(max_length=100)
   pass
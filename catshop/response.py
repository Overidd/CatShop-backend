from rest_framework import serializers
from payment_gateway.serializer import OrderDetailSerializer

#* Respuestas generales
class BAD_REQUEST(serializers.Serializer):
   message = serializers.CharField()
   error = serializers.ListField(
      child=serializers.CharField(),
      required=False,
   )

class NOT_FOUND(serializers.Serializer):
   message = serializers.CharField()

class ERROR_SERVER(serializers.Serializer):
   message = serializers.CharField()

class UNAUTHORIZED(serializers.Serializer):
   message = serializers.CharField()

#* Respuestas de autenticacion
class UserRegisterResponse(serializers.Serializer):
   message = serializers.CharField()

class ResponseTokenUser(serializers.Serializer):
   message = serializers.CharField()
   access_token = serializers.CharField()
   refresh_token = serializers.CharField()

# Respuesta de payment_gateway
class OrderDetailResponse(serializers.Serializer):
   code_order = serializers.CharField()
   total = serializers.CharField()
   total_general = serializers.CharField()
   price_delivery = serializers.CharField()
   total_discount = serializers.CharField()
   order_detail = serializers.ListField(
      child=OrderDetailSerializer(),
      required=False,
   )

class PaymentGatewayResponse(serializers.Serializer):
   message = serializers.CharField()
   data = OrderDetailResponse()

class ProcessPaymentResponse(serializers.Serializer):
   message = serializers.CharField()
   link_pdf_invoice = serializers.CharField()

class CulqiErrors(serializers.Serializer):
   type_error = serializers.CharField()
   merchant_message = serializers.CharField()
   user_message = serializers.CharField()

class ProcessPaymentError(serializers.Serializer):
   message = serializers.CharField()
   error = CulqiErrors()

class FavoritesResponse(serializers.Serializer):
   message = serializers.CharField()

class IsActiveResponse(serializers.Serializer):
   message = serializers.CharField()
   data = serializers.BooleanField()

class VerifyQuantityResponse(serializers.Serializer):
   message = serializers.CharField()
   data = serializers.BooleanField()
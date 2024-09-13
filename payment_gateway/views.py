from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
from purchases.models import (
   OrderModel,
   OrderDetailModel,
   OrderIdentificationModel,
   OrderDeliveryModel,
   OrderStoreModel,
   OrderPaymentModel,
   OrderUserTempModel
)

from profile_client.models import (
   UserClientModel,
   UserOrderModel,
)

from product.models import (
   ProductModel
)

from .serializer import (
   RegisterOrderSerializer
)

from .utils import (
   IsUserType,
   OrderType,
   OrderIdentificationType,
   OrderStoreType,
   OrderDeliveryType,
   OrderPaymentType,
   OrderDetailType,
)

class RegisterOrderView(APIView):
   def post(self, request, *args, **kwargs):
      serializer = RegisterOrderSerializer(data=request.data)
      try:
         if serializer.is_valid():
            validated_data = serializer.validated_data

            opciones_entrega = validated_data.get('opciones_entrega', {})
               
            isuser_validate = validated_data.get('isuser', {})
            isuser = IsUserType(**isuser_validate)

            order_identification_validate = validated_data.get('order_identification', {})
            order_identification = OrderIdentificationType(**order_identification_validate)

            order_store_validate = validated_data.get('order_store', {})
            order_store = OrderStoreType(**order_store_validate)

            order_delivery_validate = validated_data.get('order_delivery', {})
            order_delivery = OrderDeliveryType(**order_delivery_validate)

            order_payment_validate = validated_data.get('order_payment', {})
            order_payment = OrderPaymentType(**order_payment_validate)

            order_details_validate = validated_data.get('order_detail', [])
            order_details = [
               OrderDetailType(**item) for item in order_details_validate
            ]

            error_products = []
            is_error = False
            total = 0
            IGV = 0

            # Obtenemos los productos con el order_details id
            products = ProductModel.objects.filter(id__in=[order_delail.product_id for order_delail in order_details])

            for product in products:
               order_detail  = next((item for item in order_details  if item.product_id == product.id), None)

               if order_detail:
                  # Verificamos stock y estado
                  if product.stock < order_detail.quantity or not product.status:
                     is_error = True
                     error_products.append(product)
                  else:
                     # Calculamos el total y reducimos el stock
                     total += product.price * order_detail.quantity
                     product.stock -= order_detail.quantity
                     product.save()
            else:
               if is_error == True:
                  return Response({
                     'message': f'No es posible continuar con el pago hay algunos productos que que representa inconsistencias',
                     'data': error_products
                  }, status=status.HTTP_400_BAD_REQUEST)

            IGV = total * 0.18
            total_sin_igv = total - IGV
            new_order = OrderModel.objects.create(total=total)

            OrderIdentificationModel.objects.create(
               email = order_identification.email,
               name = order_identification.name,
               last_name = order_identification.last_name,
               document_number = order_identification.document_number,
               phone = order_identification.phone,
               ruc = order_identification.ruc,
               order = new_order.id,
            )
            OrderPaymentModel.objects.create(
               amount = total,
               payment_method = order_payment.payment_method,
               order = new_order.id,
            )

            # Generar los OrderDetails
            for product in products:
               order_detail  = next((item for item in order_details  if item.product_id == product.id), None)

               if order_detail:
                  OrderDetailModel.objects.create(
                     quantity = order_detail.quantity,
                     price = product.price,
                     product = product.id,
                     order = new_order.id,
                  )

            if isuser.isuser:
               # TODO: validar el token
               #? Vericiar si el usuario es valido
               user = UserClientModel.objects.filter(id=isuser.id_user ,email=isuser.email).first()
               if user.exists():
                  return Response({
                     'message': 'El usuario no existe',
                     'data': []
                  },status=status.HTTP_404_NOT_FOUND) 

               UserOrderModel.objects.create(order=new_order.id, user_client=user.id)
               self.registerOpcionOrder(opciones_entrega, order_store, order_delivery, new_order)

               # TODO: se podria actualizar la nueva informacion en el perfil del usario

            if not isuser.isuser:
               # En caso de que el usaurio no este registrado
               OrderUserTempModel.objects.create(email=isuser.email ,order=new_order.id)

               self.registerOpcionOrder(opciones_entrega, order_store, order_delivery, new_order)
            # Puedes hacer lo que necesites con los datos validados aquí
            return Response({
               "message": "Orden registrada exitosamente"
            }, status=status.HTTP_201_CREATED)

         return Response({
            "message": "Datos inválidos",
            "errors": serializer.errors  
         },status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
         return Response({
            "message": "Ocurrió un error inesperado",
            "error": str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         

   def registerOpcionOrder(self, opciones_entrega,  order_store, order_delivery, new_order):      
      if opciones_entrega == 'store':
         OrderStoreModel.objects.create(
            store_name = order_store.store_name,
            order = new_order.id
         )   

      if opciones_entrega == 'delivery':
         OrderDeliveryModel.objects.create(
            department = order_delivery.department,
            province = order_delivery.province,
            district = order_delivery.district,
            address = order_delivery.address,
            street = order_delivery.street,
            street_number = order_delivery.street_number,
            reference = order_delivery.reference,
            order = new_order.id,
         )
      

 
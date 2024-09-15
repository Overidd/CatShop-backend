from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import requests
from django.conf import settings

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
   RegisterOrderSerializer,
   ProcessPaymentSerializer
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

from billing.utils import invoicePayments

class RegisterOrderView(APIView):
   def post(self, request, *args, **kwargs):
      serializer = RegisterOrderSerializer(data=request.data)
      try:
         if not serializer.is_valid():
            return Response({
            "message": "Datos inválidos",
            "errors": serializer.errors  
            },status=status.HTTP_400_BAD_REQUEST)

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

         order_details_validate = validated_data.get('order_detail', [])
         order_details = [
            OrderDetailType(**item) for item in order_details_validate
         ]

         error_products = []
         is_error = False
         total = 0
         total_discount = 0

         # Obtenemos los productos con el order_details id
         products = ProductModel.objects.filter(id__in=[order_delail.product_id for order_delail in order_details])

         for product in products:
            order_detail  = next((item for item in order_details  if item.product_id == product.id), None)

            if order_detail:
               # Verificamos stock y estado del producto
               if product.stock < order_detail.quantity or not product.status:
                  is_error = True
                  error_products.append(product)

               elif is_error == False:
                  discount = product.price * (product.discount / 100)
                  price = product.price - discount
                  total_discount += discount
                  total += (product.price - discount) * order_detail.quantity

                  # Calculamos el total - discount y reducimos el stock
                  product.stock -= order_detail.quantity
                  if product.stock <= 0:
                     # Deshabilitamos el producto
                     product.status = False

                  product.save()
         else:
            if is_error == True:
               return Response({
                  'message': f'No es posible continuar con el pago hay algunos productos que representa inconsistencias',
                  'data': {
                     'error_products': error_products
                  }
               }, status=status.HTTP_400_BAD_REQUEST)

         new_order = OrderModel.objects.create(total=total, total_discount=total_discount)

         OrderIdentificationModel.objects.create(
            email = order_identification.email,
            name = order_identification.name,
            last_name = order_identification.last_name,
            document_number = order_identification.document_number,
            phone = order_identification.phone,
            ruc = order_identification.ruc,
            order = new_order.id,
         )
          # Generar los OrderDetails
         order_details_model = []
         for product in products:
            order_detail  = next((item for item in order_details  if item.product_id == product.id), None)

            if order_detail:
               discount = product.price * (product.discount / 100)
               price = product.price - discount
               subtotal = price *  order_detail.quantity

               new_order_detail = OrderDetailModel.objects.create(
                  quantity = order_detail.quantity,
                  price_unit = product.price,
                  price = price,
                  subtotal = subtotal,
                  discount = discount,
                  name_product = product.name,
                  product = product.id,
                  order = new_order.id,
               )
               order_details_model.append(new_order_detail)
         
         self.registerOpcionOrder(opciones_entrega, order_store, order_delivery, new_order)

         if isuser.isuser:
            # TODO: validar el token
            #? Vericiar si el usuario es valido
            user = UserClientModel.objects.filter(id=isuser.id_user ,email=isuser.email).first()
            if not user:
               OrderUserTempModel.objects.create(email=isuser.email ,order=new_order.id)
               return Response({
                  "message": "Orden registrada exitosamente",
                  "data": {
                     'code_order': new_order.code,
                     'total': new_order.total,
                     'total_discount': total_discount,
                     'order_detail': order_details_model
                     # 'user': user.id
                  }
               }, status=status.HTTP_201_CREATED)

            UserOrderModel.objects.create(order=new_order.id, user_client=user.id)

            # TODO: se podria actualizar la nueva informacion en el perfil del usario
         
         if not isuser.isuser:
            # En caso de que el usuario no este registrado
            OrderUserTempModel.objects.create(email=isuser.email ,order=new_order.id)
         
         return Response({
            "message": "Orden registrada exitosamente",
            "data": {
               'code_order': new_order.code,
               'total': new_order.total,
               'order_detail': order_details_model
               # 'user': user.id
            }
         }, status=status.HTTP_201_CREATED)
      
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
      

class ProcessPaymentView(APIView):   
   def post(self, request):
      serializer = ProcessPaymentSerializer(data=request.data)

      if not serializer.is_valid():
         return Response({
            "message": "Datos inválidos",
            "errors": serializer.errors
         }, status=status.HTTP_400_BAD_REQUEST)

      validated_data = serializer.validated_data

      # Obtener los datos de la orden
      order = OrderModel.objects.filter(code=validated_data['code_order']).first()

      if not order:
         return Response({
            "message": "Orden no encontrada",
         }, status=status.HTTP_404_NOT_FOUND)

      # Acceder a las relaciones OneToOne
      order_identification = order.order_identification
      order_delivery = order.order_delivery
      order_details = order.order_detail.all()

      if not order_identification or not order_delivery:
         return Response({
            "message": "Datos de identificación o datos de delivery no encontrados",
         }, status=status.HTTP_400_BAD_REQUEST)

      amount = int(order.total * 100)  # Convertir a céntimos, por ejemplo, 100.00 soles -> 10000 céntimos

      # Crear el payload para la solicitud a Culqi
      data = {
         "amount": amount,  # El monto en céntimos 
         "currency_code": "PEN",  # Moneda (PEN o USD)
         "email": order_identification.email, # Email del cliente
         "source_id": validated_data['token_id'],  # El token que se generó en el frontend
         "description": "Pago por producto",  # Descripción del cargo
         "capture": True, # Indica que la captura sea automatico, (12.00 am) procesa culqi
         "antifraud_details": {
            "address": order_delivery.address,
            "address_city": order_delivery.department,
            "country_code": "PE",
            "first_name": order_identification.name,
            "last_name": order_identification.last_name,
            "phone_number": order_identification.phone,
         },
         "metadata": {
            "order_id": order.code,
         }
      }

      # Encabezados de la solicitud
      headers = {
         "Content-Type": "application/json",
         "Authorization": f"Bearer {settings.API_KEY_CULQI}"
      }

      # Solicitud a la API de Culqi
      try:
         response = requests.post(
            settings.URL_API_CULQI,  # Api
            json=data,
            headers=headers
         )
         
         response_data = response.json() 

         if response.status_code == 201:
            source = response_data.get('source', {})
            iin = source.get('iin', {})
            issuer = iin.get('issuer', {})
            metadata = source.get('metadata', {})
    
            order_payment = OrderPaymentModel.objects.create(
               amount=amount,
               payment_method=iin.get('card_brand', 'Visa'),
               payment_number=source.get('card_number', 0),
               card_type = iin.get('card_type', 'Debito'),
               card_name = issuer.get('name', None),
               country_code = issuer.get('country_code', None),
               installments = metadata.get('installments', 1),
               order=order.id
            )
            order.status = True
            order.save()

            # TODO: Enviar email de seguimiento al cliente y administrador
            # TODO: Generar facturacion de los productos comprados y enviar un email al cliente
            link_pdf_invoice = invoicePayments(order_identification, order_delivery, order_payment, order_details)

            return Response({
               "message": "Pago realizado exitosamente",
               'data': {
                  "link_pdf_invoice": link_pdf_invoice
               }
            }, status=status.HTTP_201_CREATED)
         
         else:
             return Response({
               "message": "Ocurrió un error al procesar el pago",
               "errors": {
                  "type_error": response_data['type'],
                  "merchant_message": response_data['merchant_message'],
                  "user_message": response_data['user_message'],
               }},status=response.status_code)

      except requests.RequestException as e:
         return Response({
            "message": "Ocurrió un error inesperado",
            "error": str(e),
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


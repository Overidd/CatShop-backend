from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

import requests
from django.conf import settings
from hashids import Hashids
hashids = Hashids(salt="sdf78Pxq34lZsada", min_length=6)

import uuid

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
   UserPaymentMethodModel,
   UserAddressModel,
)

from product.models import (
   ProductModel
)

from .serializer import (
   RegisterOrderSerializer,
   ProcessPaymentSerializer,
   OrderDetailSerializer,
   ProductModelSerializer
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
from django.core.mail import send_mail

class RegisterOrderView(CreateAPIView):
   serializer_class = RegisterOrderSerializer
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

         order_details_validate = validated_data.get('order_details', [])
         order_details = [
            OrderDetailType(**item) for item in order_details_validate
         ]
         error_products_unserialized = []
         is_error = False
         total = 0
         total_discount = 0
         price_delivery = 0

         # Obtenemos los productos con el order_details id
         products = ProductModel.objects.filter(id__in=[order_delail.product_id for order_delail in order_details])
         
         for product in products:
            order_detail  = next((item for item in order_details  if item.product_id == product.id), None)

            if order_detail:
               # Verificamos stock y estado del producto
               if product.stock < order_detail.quantity or not product.status:
                  is_error = True
                  error_products_unserialized.append(product)

               elif is_error == False:
                  discount = round(product.price * (product.discount / 100), 2)
                  total_discount += discount * order_detail.quantity
                  total += (product.price - discount) * order_detail.quantity

                  # Calculamos el total - discount y reducimos el stock
                  product.stock -= order_detail.quantity
                  if product.stock <= 0:
                     # Deshabilitamos el producto
                     product.status = False

                  product.save()
         else:
            if is_error == True:
               error_products = ProductModelSerializer(error_products_unserialized, many=True).data
               return Response({
                  'message': f'No es posible continuar con el pago hay algunos productos que representa inconsistencias',
                  'data': {
                     'error_products': error_products
                  }
               }, status=status.HTTP_400_BAD_REQUEST)

         new_order = OrderModel.objects.create(
            total=round(total,2), 
            total_discount=round(total_discount,2),
         )

         is_order_store, is_order_delivery = self.registerOpcionOrder(opciones_entrega, order_store, order_delivery, new_order)
         if is_order_delivery:
            #TODO: Se asignar manualmente el precio por delivery en 20
            price_delivery = 20

         new_code = 'order-'+ hashids.encode(new_order.id)
         new_order.code = new_code
         new_order.price_delivery = price_delivery
         new_order.save()

         OrderIdentificationModel.objects.create(
            email = order_identification.email,
            name = order_identification.name,
            last_name = order_identification.last_name,
            document_number = order_identification.document_number,
            phone = order_identification.phone,
            ruc = order_identification.ruc,
            order = new_order,
         )

         # Generar los OrderDetails
         order_details_unserialized = []
         for product in products:
            order_detail  = next((item for item in order_details  if item.product_id == product.id), None)

            if order_detail:
               discount = round(product.price * (product.discount / 100), 2)
               price_final = product.price - discount
               subtotal = price_final * order_detail.quantity

               new_order_detail = OrderDetailModel.objects.create(
                  quantity = order_detail.quantity,
                  price_unit = product.price,
                  price_final = round(price_final,2),
                  subtotal = round(subtotal,2),
                  discount = discount,
                  name_product = product.name,
                  product = product,
                  order = new_order,
               )
               new_order_detail.code = 'detail-'+ hashids.encode(new_order_detail.id)
               new_order_detail.save()
               order_details_unserialized.append(new_order_detail)

         order_details_data = OrderDetailSerializer(order_details_unserialized, many=True).data

         if isuser.isuser:
            # TODO: validar el token
            #? Verificar si el usuario es valido
            user = UserClientModel.objects.filter(id=isuser.id_user ,email=isuser.email).first()
            if not user:
               OrderUserTempModel.objects.create(email=isuser.email ,order=new_order)
               return Response({
                  "message": "Orden registrada exitosamente",
                  "data": {
                     'code_order': new_order.code,
                     'total': new_order.total,
                     'total_general': new_order.total + price_delivery ,
                     'price_delivery': price_delivery,
                     'total_discount': new_order.total_discount,
                     'order_detail': order_details_data,
                  }
               }, status=status.HTTP_201_CREATED)

            UserOrderModel.objects.create(
               order=new_order, 
               user_client=user,
            )

            # TODO: Se actualiza la nueva informacion en el perfil del usario      
            
            if hasattr(user, 'user_address') and user.user_address:
               user_address = user.user_address
               user_address.department = order_delivery.department
               user_address.province = order_delivery.province
               user_address.district = order_delivery.district
               user_address.address = order_delivery.address
               user_address.street = order_delivery.street
               user_address.street_number = order_delivery.street_number
               user_address.reference = order_delivery.reference
               user_address.save()
            else:
               # Crear una nueva dirección
               UserAddressModel.objects.create(
                  user_client=user,
                  department=order_delivery.department,
                  province=order_delivery.province,
                  district=order_delivery.district,
                  address=order_delivery.address,
                  street=order_delivery.street,
                  street_number=order_delivery.street_number,
                  reference=order_delivery.reference,
               )

         
         if not isuser.isuser:
            # En caso de que el usuario no este registrado
            OrderUserTempModel.objects.create(
               email=order_identification.email,
               order=new_order
            )
         
         return Response({
            "message": "Orden registrada exitosamente",
            "data": {
               'code_order': new_order.code,
               'total': new_order.total,
               'total_general': new_order.total + price_delivery ,
               'price_delivery': price_delivery,
               'total_discount': new_order.total_discount,
               'order_detail': order_details_data,
               # 'user': user.id
            }
         }, status=status.HTTP_201_CREATED)
      
      except Exception as e:

         return Response({
            "message": "Ocurrió un error inesperado",
            "error": str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         

   def registerOpcionOrder(self, opciones_entrega,  order_store, order_delivery, new_order):   
      new_order_store = None
      new_order_delivery = None
      if opciones_entrega == 'store':
         new_order_store = OrderStoreModel.objects.create(
            store_name = order_store.store_name,
            order = new_order
         )   

      if opciones_entrega == 'delivery':
         new_order_delivery = OrderDeliveryModel.objects.create(
            department = order_delivery.department,
            province = order_delivery.province,
            district = order_delivery.district,
            address = order_delivery.address,
            street = order_delivery.street,
            street_number = order_delivery.street_number,
            reference = order_delivery.reference,
            order = new_order,
         )
      return new_order_store, new_order_delivery
   
   def generate_unique_code(self):
      # Genera un UUID4 para asegurar unicidad
      unique_id = uuid.uuid4().int
      # Codifica el UUID4 como un código corto
      return hashids.encode(unique_id)

class IsOrderDelivery:
   def __init__(self, address, department):
      self.address = address if address !='none' or address else "Tienda"
      self.department = department


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

      order_delivery = IsOrderDelivery('Tienda', 'Tienda')
      if hasattr(order, 'order_store') and order.order_store:
         order_delivery = IsOrderDelivery(order.order_store, '')

      if hasattr(order, 'order_delivery') and order.order_delivery:
         order_delivery = IsOrderDelivery(order.order_delivery, '')

      if not order_identification or not order_delivery:
         return Response({
            "message": "Datos de identificación o datos de delivery no encontrados",
         }, status=status.HTTP_400_BAD_REQUEST)

      amount = int((order.total * 100) + order.price_delivery)  # Convertir a céntimos, por ejemplo, 100.00 soles -> 10000 céntimos
      # print(order_delivery.address, 'order_delivery')
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
            # "address_city": order_delivery.department,
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

            
            order_payment = OrderPaymentModel.objects.filter(order=order).first()

            if order_payment:
               # Si ya existe, actualiza los datos del pago
               order_payment.amount = amount
               order_payment.payment_method = iin.get('card_brand', 'Visa')
               order_payment.payment_number = source.get('card_number', 0)
               order_payment.card_type = iin.get('card_type', 'Debito')
               order_payment.card_name = issuer.get('name', None)
               order_payment.country_code = issuer.get('country_code', None)
               order_payment.installments = metadata.get('installments', 1)
               order_payment.save()
            else:
               # Si no existe, crea un nuevo registro de pago
               order_payment = OrderPaymentModel.objects.create(
                  amount=amount,
                  payment_method=iin.get('card_brand', 'Visa'),
                  payment_number=source.get('card_number', 0),
                  card_type=iin.get('card_type', 'Debito'),
                  card_name=issuer.get('name', None),
                  country_code=issuer.get('country_code', None),
                  installments=metadata.get('installments', 1),
                  order=order
               )
            order.status = True
            order.save()

            if validated_data.get('is_user_id'):
               user_payment = UserPaymentMethodModel.objects.filter(user_client=validated_data.get('is_user_id')).first()

               if user_payment:
                  user_payment.payment_method = order_payment.payment_method
                  user_payment.payment_number = order_payment.payment_number
                  user_payment.card_type = order_payment.card_type
                  user_payment.card_name = order_payment.card_name
                  user_payment.country_code = order_payment.country_code
                  user_payment.installments = order_payment.installments
                  user_payment.save()

               
            # TODO: Enviar email de seguimiento al cliente y administrador
            # TODO: Generar facturacion de los productos comprados 
            link_pdf_invoice = invoicePayments(order, order_identification, order_delivery, order_payment)
            
            # TODO: Enviar un email al cliente   
            subject='Pago realizado con éxito'
            message=f'Se ha realizado un pago exitoso en la orden {order.code}. Por favor, verifica tu información de pago en el link: {link_pdf_invoice}'
            recipient = order_identification.email
            send_mail(
               subject,
               message,
               'noreply@localhost.com',
               [recipient],
               fail_silently = False
            )

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



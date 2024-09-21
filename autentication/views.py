from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from django.core.mail import send_mail
from django.template.loader import render_to_string # Para renderizar contenido html
from django.db import transaction
from profile_client.models import UserClientModel

from purchases.models import OrderModel, OrderUserTempModel

from rest_framework.generics import (
   GenericAPIView,
   ListAPIView,
   CreateAPIView,
)

from profile_client.models import (
   UserClientModel, 
   UserAddressModel, 
   UserPaymentMethodModel, 
   UserOrderModel,
   RoleModel,
)

from .serializers import (
   UsertokenSerializer,
   UserEmailSerializer, 
   UserRegisterSerializer, 
   UserLoginSerializer, 
   ResendCodeSerializer,
   RoleSerializer
)

from catshop.response import (
   UserRegisterResponse,
   ResponseTokenUser,
   BAD_REQUEST,
   ERROR_SERVER,
   NOT_FOUND,
   UNAUTHORIZED,
)

import random
from drf_yasg.utils import swagger_auto_schema


def email_code_verification(user, verification_code):
   subject = f'Hola {user.name}, Confirma tu cuenta CatShop'
   recipient = [user.email]
   html_verification_code = render_to_string('catShop_codigo_verificacion.html', {
      'name': user.name,
      'email': user.email,
      'code': verification_code
   })

   send_mail(
      subject,
      '',  # Mensaje de texto plano
      'noreply@localhost.com',  # Remitente
      recipient,  # Destinatario
      html_message=html_verification_code,  # Mensaje en HTML
      fail_silently=False
   )

def email_welcome(user):
   subject = f'Hola {user.name}, Bienvenido a CatShop'
   recipient = [user.email]
   html_welcome = render_to_string('catShop_correo_verificado.html', {
      'name': user.name
   }) # Rendizar el html

   send_mail(
      subject,
      '',
      'noreply@localhost.com', 
      recipient,  # 
      html_message=html_welcome, # El mensaje con html
      fail_silently=False 
   )

class UserRegisterView(GenericAPIView):
   serializer_class = UserRegisterSerializer

   @swagger_auto_schema(
      request_body=UserRegisterSerializer,
      responses={
         201: UserRegisterResponse,
         400: BAD_REQUEST,
         500: ERROR_SERVER,
      }
    )
   @transaction.atomic
   def post(self, request):
      try:
         serializer = self.serializer_class(data=request.data)
         serializer.is_valid(raise_exception=True)

         # Verificar si el usuario ya existe
         email = serializer.validated_data['email']
         if UserClientModel.objects.filter(email=email).exists():
            return Response({
               "message": "El email ya se encuentra registrado.",
               "error": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

         # Generar el código de verificación
         verification_code = str(random.randint(1000, 9999))

         # Crear el usuario usando el método create del serializador
         user = serializer.save(
            verification_code=verification_code,
            is_verified=False
         )

      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "error": e.detail
         }, status=status.HTTP_400_BAD_REQUEST)

      except Exception as e:
         return Response({
            "message": "Ocurrió un error",
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      try:
        # Enviar el código de verificación al email del usuario después de la transacción
         email_code_verification(user, verification_code)

         return Response({
               "message": "Usuario registrado. Verifica tu email con el código enviado."
         }, status=status.HTTP_201_CREATED)
      
      except Exception as e:
         return Response({
            "message": "Usuario creado, pero ocurrió un error al enviar el correo de verificación.",
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(GenericAPIView): 
   serializer_class = UserEmailSerializer
   
   @swagger_auto_schema(
      request_body=UserEmailSerializer,
      responses={
         200: ResponseTokenUser,
         400: BAD_REQUEST,
         500: ERROR_SERVER,
      }
    )
   
   @transaction.atomic
   def post(self, request):
      serializer = self.serializer_class(data=request.data)
      serializer.is_valid(raise_exception=True)
      validated_data = serializer.validated_data
      
      try:
         # Verificar si el usuario existe y si el código es correcto
         user = UserClientModel.objects.get(email=validated_data['email'], verification_code=validated_data['verification_code'])

      except UserClientModel.DoesNotExist:
         return Response({
            "message": "Código incorrecto",
            "error": "error"
         }, status=status.HTTP_400_BAD_REQUEST)
   
      user.is_verified = True
      user.verification_code = None 
      user.save()
      
      # Generar un token (usando JWT)
      token = UsertokenSerializer.get_tokens_user(user)
      
      # TODO: Recuperar el historial del usuario
      try:
         isOrderUser = OrderUserTempModel.objects.filter(email=user.email)

         if isOrderUser.exists(): 
            orders = OrderModel.objects.filter(id__in=[orderUser.order_id for orderUser in isOrderUser]).order_by('-created_at')

            if orders:
               # Actualizar los datos del usuario con la identificación del pedido más reciente
               latest_order = orders[0]

               if  hasattr(latest_order, 'order_identification'):         
                  identification = latest_order.order_identification
                  user.last_name = identification.last_name
                  user.document_number = identification.document_number
                  user.phone = identification.phone
                  user.ruc = identification.ruc
                  user.save()

               # Crear la dirección del usuario
               if hasattr(latest_order, 'order_delivery'):
                  address = latest_order.order_delivery
                  UserAddressModel.objects.create(
                     department=address.department,
                     province=address.province,
                     district=address.district,
                     address=address.address,
                     street=address.street,
                     street_number=address.street_number,
                     reference=address.reference,
                     user_client=user
                  )

               # Guardar el historial de pedidos y los métodos de pago
               for order in orders:
                  UserOrderModel.objects.create(
                     order=order,
                     user_client=user
                  )

                  if hasattr(order, 'order_payment') and order.order_payment:
                     payment = order.order_payment
                     UserPaymentMethodModel.objects.create(
                        amount=payment.amount,
                        payment_method=payment.payment_method,
                        payment_number=payment.payment_number,
                        card_type = payment.card_type,
                        card_name = payment.card_name,
                        country_code = payment.country_code,
                        installments  = payment.installments,
                        user_client=user,
                     )

         #TODO Se envia un email de bienvenida al cliente
         email_welcome(user)
            
         return Response({
            "message": "Verificación completada",
            "access_token": token['access'],
            "refresh_token": token['refresh']
         }, status=status.HTTP_200_OK)

      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "error": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)

      except Exception as e:
         return Response({
            "message": "Ocurrió un error inesperado",
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserloginView(GenericAPIView):
   serializer_class = UserLoginSerializer

   @swagger_auto_schema(
      request_body=UserLoginSerializer,
      responses={
         200: ResponseTokenUser,
         400: BAD_REQUEST,
         401: UNAUTHORIZED,
         404: NOT_FOUND,
         500: ERROR_SERVER,
      }
   )
   
   def post(self, request):
      try:
         serializer  = self.serializer_class(data=request.data)
         serializer .is_valid(raise_exception=True)
         validated_data = serializer.validated_data

         user = UserClientModel.objects.get(email=validated_data["email"])
         
         # Verificar si la cuenta del usuario esta vetificado
         if not user.is_verified:
            return Response({
                "message": "Cuenta no verificada",
            }, status=status.HTTP_400_BAD_REQUEST)
         
         # Verificar la contraseña del usuario
         if not check_password(validated_data["password"], user.password):
            return Response({
               "message": "Contraseña incorrecta",
            }, status=status.HTTP_401_UNAUTHORIZED)

         return Response({
            "message": "Login correcto",
            "access_token": UsertokenSerializer.get_tokens_user(user)['access'],
            "refresh_token": UsertokenSerializer.get_tokens_user(user)['refresh']
            }, status=status.HTTP_200_OK)
      
      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "error": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)      
      
      except UserClientModel.DoesNotExist:
         return Response({
            "message": "unauthenticated",
         }, status=status.HTTP_401_UNAUTHORIZED)

      except Exception as e:
         return Response({
            "message": "Ocurrió un error inesperado",
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendCodeView(GenericAPIView):
   serializer_class = ResendCodeSerializer

   @swagger_auto_schema(
      request_body=ResendCodeSerializer,
      responses={
         200: ResponseTokenUser,
         400: BAD_REQUEST,
         404: NOT_FOUND,
         500: ERROR_SERVER,
      }
   )
   def post(self, request):
      try:
         serializer = self.serializer_class(data=request.data)
         serializer.is_valid(raise_exception=True)
         validated_data = serializer.validated_data

         #Verificar si existe una cuenta
         user = UserClientModel.objects.get(email=validated_data['email'])
         if not user.is_verified:
            return Response({
                "message": "unauthorized",
            }, status=status.HTTP_404_NOT_FOUND)
         
         # Generar nuevo codigo de verificación
         verification_code = str(random.randint(1000, 9999))         
         user.verification_code = verification_code
         user.is_verified = False
         user.save()

         # Volver a enviar codigo de verificación
         email_code_verification(user, verification_code)

         return Response({
            "message": "Código de verificación enviado correctamente"
         }, status=status.HTTP_200_OK)   
         
      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "errors": e.detail
         }, status=status.HTTP_400_BAD_REQUEST)

      except Exception as e:
         return Response({
            "message": "Ocurrió un error inesperado",
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         

class UserRegisterGoogleView(APIView):
   pass

class RoleListView(ListAPIView):
    queryset = RoleModel.objects.all()
    serializer_class = RoleSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return Response({
            'message': 'Roles fetched successfully',
            'data': response.data
        }, status=status.HTTP_200_OK)
    
class RoleCreateView(CreateAPIView):
    serializer_class = RoleSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response({
            'message': 'Role created successfully',
            'data': response.data
        }, status=status.HTTP_201_CREATED)
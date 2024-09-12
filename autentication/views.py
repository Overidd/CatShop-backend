from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from django.core.mail import send_mail

from profile_client.models import UserClientModel
from purchases.models import OrderModel, OrderUserTempModel

from .serializers import (
   UsertokenSerializer, UserEmailSerializer, UserRegisterSerializer, UserLoginSerializer
)
import random

from django.shortcuts import render

class UserRegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True) # Para ValidationError 
            
            # Verificar si el usuario existe
            email = serializer.validated_data['email']
            if UserClientModel.objects.filter(email=email).exists():
                return Response({
                    "message": "El email ya se encuentra registrado."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generar el codigo
            verification_code = str(random.randint(1000, 9999))

            # Enviar el código de verificación al gmail del usuario
            subject = f'Hola {serializer.validated_data["name"]}, Confirma tu cuenta CatShop'
            message = f'Tu código de verificación es: {verification_code}'
            recipient = [serializer.validated_data['email']]
            
            send_mail(
                subject,
                message,
                'noreply@localhost.com',  # El remitente 
                recipient,  # A quienes se los envía
                fail_silently=False  # Mostrar una excepción cuando ocurra un error al enviar el correo 
            )
            
            # Crear el usuario usando el método create del serializador
            serializer.save(
               verification_code=verification_code,
               is_verified=False
            )

            return Response({
                "message": "Usuario registrado. Verifica tu email con el código enviado."
            }, status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            return Response({
                "message": "Datos inválidos",
                "errors": e.detail 
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "message": "Ocurrió un error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegisterGoogleView(APIView):
   pass

class VerifyEmailView(APIView):
   def post(self, request):
      try:
         serializer = UserEmailSerializer(data=request.data)
         serializer.is_valid(raise_exception=True)
         validated_data = serializer.validated_data
         
         user = UserClientModel.objects.get(email=validated_data['email'], verification_code=validated_data['verification_code'])
         
         if not user.is_verified:
            return Response({
                "message": "El código de verificación es incorrecto"
            }, status=status.HTTP_400_BAD_REQUEST)

         # Actualizar los campos de verificacion de usuario
         user.is_verified = True
         user.verification_code = None  # Eliminar el código de verificación
         user.save()

         #TODO: Generar un token (usando JWT)
         token = UsertokenSerializer.get_tokens_user(user)


         # TODO: Recuperar el historial del usuario | OrderMode, OrderUserTempModel |
         # isOrderUser = OrderUserTempModel.objects.filter(email= validated_data['email'])
         # if isOrderUser:
            # userOrderInfo = OrderModel.objects.filter(order=isOrderUser)

         return Response({
            "message": "Verificación completada",
            "access_token": token['access'],
            "refresh_token": token['refresh']
         }, status=status.HTTP_200_OK)

      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "errors": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)      
      
      except Exception as e:
          return Response({
              "message": "Ocurrió un error inesperado",
              "error": str(e)
          }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      


class UserloginView(APIView):
   def post(self, request):
      try:
         serializer  = UserLoginSerializer(data=request.data)
         serializer .is_valid(raise_exception=True)
         validated_data = serializer.validated_data

         user = UserClientModel.objects.get(email=validated_data["email"])
         
         # Verificar si la cuenta del usuario esta vetificado
         if not user.is_verified:
            return Response({
                "message": "Cuenta no verificada",
            }, status=status.HTTP_400_BAD_REQUEST)
         
         if not check_password(validated_data["password"], user.password):
            return Response({
                "message": "Contraseña incorrecta",
            }, status=status.HTTP_400_BAD_REQUEST)

         return Response({
            "message": "Login correcto",
            "access_token": UsertokenSerializer.get_tokens_user(user)['access'],
            "refresh_token": UsertokenSerializer.get_tokens_user(user)['refresh']
            }, status=status.HTTP_200_OK)
      
      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "errors": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)      
      
      except UserClientModel.DoesNotExist:
         return Response({
            "message": "unauthenticated",
         }, status=status.HTTP_404_NOT_FOUND)

      except Exception as e:
         return Response({
            "message": "Ocurrió un error inesperado",
            "error": str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
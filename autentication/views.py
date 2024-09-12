from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from django.core.mail import send_mail

from profile_client.models import UserClientModel
from .serializers import (
   UsertokenSerializer, UserEmailSerializer, UserRegisterSerializer, UserLoginSerializer
)
import random

from django.shortcuts import render
class UserRegisterView(APIView):
   def post(self, request):
      try: 
         serializer = UserRegisterSerializer(data=request.data)
         serializer.is_valid(raise_exception=True)  # Levanta ValidationError si falla
         validated_data = serializer.validated_data

         # Verificar si el usuario ya esta registrado
         email = validated_data.validated_data['email']
         if UserClientModel.objects.filter(email=email).exists():
            return Response({
               "message": "El email ya se encuentra registrado."
            }, status=status.HTTP_400_BAD_REQUEST)

         # Crear el código de verificación
         verification_code = str(random.randint(1000, 9999))
         
         # Enviar el código de verificación por correo electrónico
         subject = f'Hola {validated_data.validated_data["name"]}, Confirma tu cuenta CatShop'
         message = f'Tu código de verificación es: {verification_code}'
         recipient = [validated_data.validated_data['email']]

         send_mail(
            subject,
            message,
            'noreply@localhost.com',  #: El remitente (correo desde el que se envía el correo).
            recipient, # A quienes se los envia
            fail_silently=False # Controla si se debe mostrar una excepción cuando ocurra un error al enviar el correo (False significa que se mostrará el error
         )
         
         # Crear el usuario pero sin verificar
         UserClientModel.objects.create(
            name=validated_data.validated_data['name'],
            email=validated_data.validated_data['email'],
            password=validated_data.validated_data['password'],  # Ya encriptada por el serializador
            verification_code=verification_code,
            is_verified=False
         )

         return Response({
            "message": "Usuario registrado. Verifica tu email con el código enviado."
            }, status=status.HTTP_201_CREATED)
      
      except serializers.ValidationError as e:
            return Response({
                "message": "Datos inválidos",
                "errors": e.detail  # Detalles de los errores de validación
            }, status=status.HTTP_400_BAD_REQUEST)
      
      except Exception as e:
         return Response({
            "message": "ocurrio un error",
            "error": str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserRegisterGoogleView(APIView):
   pass

class VerifyEmailView(APIView):
    def post(self, request):
        try:
            # Instanciar el serializador con los datos proporcionados
            serializer = UserEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            # Validar si el email y el código de verificación existen en la base de datos
            user = UserClientModel.objects.get(
                email=validated_data.validated_data['email'],
                verification_code=validated_data.validated_data['verification_code']
            )

            # Actualizar los campos de verificación de usuario
            user.is_verified = True
            user.verification_code = None  # Eliminar el código de verificación
            user.save()

            # TODO: Generar un token (usando JWT)
            token = UsertokenSerializer.get_tokens_user(user)

            return Response({
                "message": "Verificación completada",
                "access_token": token['access'],
                "refresh_token": token['refresh']
            }, status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            # Capturar y manejar los errores de validación del serializador
            return Response({
                "message": "Datos inválidos",
                "errors": e.detail  # Detalles de los errores de validación
            }, status=status.HTTP_400_BAD_REQUEST)

        except UserClientModel.DoesNotExist:
            # Capturar cuando no se encuentra el usuario en la base de datos
            return Response({
                "message": "Código de verificación incorrecto",
                "error": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Capturar cualquier otro tipo de error inesperado
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

         if not user.check_password(validated_data["password"]):
            return Response({
                "message": "Contraseña incorrecta",
            }, status=status.HTTP_400_BAD_REQUEST)

         return Response({
            "message": "Login correcto",
            "access_token": UsertokenSerializer.get_tokens_user(user)['access'],
            "refresh_token": UsertokenSerializer.get_tokens_user(user)['refresh']
            }, status=status.HTTP_200_OK)
      
      except user.DoesNotExist:
         return Response({
            "message": "unauthenticated",
         }, status=status.HTTP_404_NOT_FOUND)

      except Exception as e:
         return Response({
            "message": "Ocurrió un error inesperado",
            "error": str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
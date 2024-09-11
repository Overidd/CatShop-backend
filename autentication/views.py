from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password  # Import para encriptar la contraseña

from profile_client.models import UserClientModel
from .serializer import UsertokenSerializer

import random

class UserRegisterView(APIView):
   def post(self, request):
      try: 
         # Datos requeridos para crear una cuenta
         name = request.data.get('name')
         email = request.data.get('email')
         password = request.data.get('password')

         # Verificar si el usuario ya esta registrado
         if UserClientModel.objects.filter(email=email).exists():
            return Response({
                "message": "El email ya se encuentra registrado."
            }, status=status.HTTP_400_BAD_REQUEST)

         # Crear el codigo de verificacion
         verification_code = str(random.randint(1000,9999))

         # Encriptar la contraseña antes de almacenarla
         encrypted_password = make_password(password)
         print(encrypted_password)

         # Enviar el codigo de verificacion por correo electronico
         subject = f'Hola {name}, Confirma tu cuenta CatShop'
         message = f'Tu código de verificación es: {verification_code}'
         recipient = [email]

         send_mail(
            subject,
            message,
            'noreply@localhost.com',  #: El remitente (correo desde el que se envía el correo).
            recipient, # A quienes se los envia
            fail_silently=False # Controla si se debe mostrar una excepción cuando ocurra un error al enviar el correo (False significa que se mostrará el error
         )
         
         # Crear el usuario pero sin verificar
         UserClientModel.objects.create(
            name=name,
            email=email,
            password=encrypted_password,
            verification_code=verification_code,
            is_verified=False
         )
         return Response({
            "message": "Usuario registrado. Verifica tu email con el código enviado."
            }, status=status.HTTP_201_CREATED)
      
      except Exception as e:
         return Response({
            "message": "ocurrio un error",
            "error": str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserRegisterGoogleView(APIView):
   pass


class VerifyEmailView(APIView):
   def post(self, request):
      email = request.data.get('email')
      verification_code = request.data.get('verification_code')
      try:
         # Validar si el email y el codigo de verificacion existe en la base de datos 
         user = UserClientModel.objects.get(email=email, verification_code=verification_code)
   
      except UserClientModel.DoesNotExist:
          return Response({
             "message": "Código de incorrecto",
             "error": "error"
          }, status=status.HTTP_400_BAD_REQUEST)
      
      # Actualizar los campos de verificacion de usuario
      user.is_verified = True
      user.verification_code = None  # Eliminar el código de verificación
      user.save()

      #TODO: Generar un token (usando JWT)
      token = UsertokenSerializer.get_tokens_user(user)

      return Response({
         "message": "Verificación completada",
         "access_token": token['access'],
         "refresh_token": token['refresh']
      }, status=status.HTTP_200_OK)
 
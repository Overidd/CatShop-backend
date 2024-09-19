from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from profile_client.models import UserClientModel, RoleModel

from django.contrib.auth.hashers import make_password 
# Función para crear el token con el correo electrónico añadido al payload
from rest_framework_simplejwt.tokens import RefreshToken
class UsertokenSerializer():
   @staticmethod
   def get_tokens_user(user):
      refresh = RefreshToken.for_user(user)
      
      # Añadir email al token
      refresh['user_id'] = user.id
      refresh['email'] = user.email
      refresh['name'] = user.name
      
      return {
         'refresh': str(refresh),
         'access': str(refresh.access_token),
      }

class UserRegisterSerializer(ModelSerializer):
   password = serializers.CharField(write_only=True, required=True, allow_blank=False)

   class Meta:
      model = UserClientModel
      fields = ['name', 'email', 'password']  # Definir los campos explícitamente
      extra_kwargs = {
         'password': {'write_only': True},
      }
    
   # Este método se utiliza para encriptar la contraseña antes de guardarla
   def validate_password(self, value):
      return make_password(value)
   
   def to_representation(self, instance):
     representation = super().to_representation(instance)
     
     representation.pop('password', None)
     return representation

class UserEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)
    

class UserLoginSerializer(serializers.Serializer):
   email = serializers.EmailField()
   password = serializers.CharField()

class ResendCodeSerializer(serializers.Serializer):
   email = serializers.EmailField()

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleModel
        fields = '__all__'

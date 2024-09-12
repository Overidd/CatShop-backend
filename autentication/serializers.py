from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ModelSerializer
from profile_client.models import UserClientModel

# Función para crear el token con el correo electrónico añadido al payload
from django.contrib.auth.hashers import make_password 
class UsertokenSerializer():
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
   class Meta:
      model = UserClientModel
      fields = ['name', 'email', 'password']

    # Este método se utiliza para encriptar la contraseña antes de guardarla
   def validate_password(self, value):
        return make_password(value)
   
class UserEmailSerializer(ModelSerializer):
    class Meta:
      model = UserClientModel
      fields = ['emain', 'verification_code']

class UserLoginSerializer(ModelSerializer):
   class Meta:
      model = UserClientModel
      fields = ['email', 'password']

from rest_framework_simplejwt.tokens import RefreshToken

# Función para crear el token con el correo electrónico añadido al payload

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

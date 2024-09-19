import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

def decode_jwt_token(token):
    try:
        token_user = token.replace('Bearer ', '')
        # Decodificar el token JWT
        decoded_token = jwt.decode(
            token_user, 
            settings.SECRET_KEY,  # Asegúrate de que estás usando la clave correcta
            algorithms=["HS256"]
        )
        return decoded_token
    
    except jwt.ExpiredSignatureError:
        return Response({
            "message": "unauthorized"
        },
        status=status.HTTP_401_UNAUTHORIZED)
    
    except jwt.InvalidTokenError:
        return Response({
            "message": "unauthorized"
        },
        status=status.HTTP_401_UNAUTHORIZED)


import jwt
from django.conf import settings

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
        raise "Token expirado"
    
    except jwt.InvalidTokenError:
        raise  "Token inválido"

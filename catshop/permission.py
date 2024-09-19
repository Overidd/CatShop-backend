from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission

def custom_exception_handler(exc, context):
   response = exception_handler(exc, context)

   # Manejar errores de autenticación (falta de token o token inválido)
   if isinstance(exc, NotAuthenticated):
      custom_response_data = {
         'message': 'Unauthorized',
      }
      return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

   if isinstance(exc, AuthenticationFailed):
      custom_response_data = {
         'message': 'Unauthorized',
      }
      return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

   return response

class IsAdmin(BasePermission):
   def has_permission(self, request, view):      
      if request.user.role_id.name != 'ADMIN':
         raise AuthenticationFailed(detail={
             'message': 'Unauthorized'
         }, code=401)

      return True
    

class IsClient(BasePermission):
    def has_permission(self, request, view):
      if request.user.role_id.name != 'CLIENT':
         raise AuthenticationFailed(detail={
             'message': 'Unauthorized'
         }, code=401)

      return True
    
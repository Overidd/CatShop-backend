from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.generics import (
   CreateAPIView,
   DestroyAPIView,
   ListAPIView,
   UpdateAPIView,
   GenericAPIView
)
from .models import (
   UserFavoritesModel,
   UserClientModel,
   UserAddressModel
)
from .serializers import (
   UserFavoritesSerializer, 
   UserDetailSerializer,
   UserClientSerializer,
   UserAddressSerializer
)

from product.serializer import ProductListSerializer


from autentication.utils import decode_jwt_token
#* Importamos el model product
from product.models import ProductModel

class GetallFavoriteView(ListAPIView):
   queryset = UserFavoritesModel.objects.all()
   serializer_class = ProductListSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación

   def list(self, request, *args, **kwargs):
      try:
         idUser = kwargs.get('pk')
         if not idUser or not idUser.isdigit():
            return Response({
               'message': 'Envia el id el usuario',
            }, status=status.HTTP_400_BAD_REQUEST)

         user_favorites = self.queryset.filter(user_client_id=idUser)

         if not user_favorites.exists():
            return Response({
               'message': 'No hay productos favoritos',
            }, status=status.HTTP_404_NOT_FOUND)

         product_ids = user_favorites.values_list('product_id', flat=True)
         product_favorites = ProductModel.objects.filter(id__in=product_ids, stock__gt=0, status=True)

         products = ProductListSerializer(data=product_favorites, many=True).data
         return Response({
            'message': 'Productos favoritos obtenidos correctamente',
            'data': products,
         }, status=status.HTTP_200_OK)

      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestroyFavoriteView(DestroyAPIView):
   queryset = UserFavoritesModel.objects.all()
   serializer_class = UserFavoritesSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación
   def destroy(self, request, *args, **kwargs):
      try:
         id = kwargs.get('pk')
         if not id:
            return Response({
               'message': 'Debe proporcionar un id'
            }, status=status.HTTP_400_BAD_REQUEST)

         user_favorite = self.queryset.get(id=id)
         user_favorite.delete()

         return Response({
            'message': 'Producto eliminado de favoritos correctamente',
         }, status=status.HTTP_204_NO_CONTENT)

      except UserFavoritesModel.DoesNotExist:
         return Response({
            'message': 'Producto favorito no encontrado',
         }, status=status.HTTP_404_NOT_FOUND)
      
      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateFavoriteView(CreateAPIView):
   serializer_class = UserFavoritesSerializer

   def create(self, request, *args, **kwargs):
      response = super().create(request, *args, **kwargs)

      return Response({
         'message': 'Agregado como producto favorito',
         'data': response.data,
      }, status=status.HTTP_201_CREATED)
   
#TODO Obtener toda la información almacenado del usuario con el id usuario 
class GetUserByIdView(ListAPIView):
   queryset = UserClientModel.objects.all()
   serializer_class = UserDetailSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación

   def get(self, request, *args, **kwargs):
      try:
         idUser = kwargs.get('pk')
         if not idUser:
            return Response({
               'message': 'Debe proporcionar un id'
            }, status=status.HTTP_400_BAD_REQUEST)
         
         user = self.queryset.get(id=idUser)
         addresses = user.user_address.all()
         payment_methods = user.user_payment.all() 
         user_orders = user.user_client.all()  # 'user_client' es el related_name en UserOrderModel

         #* Obtiene las filas de OrderModel que esten relacionados con user_orders
         orders = [user_order.order for user_order in user_orders]

         return Response({
            'message': 'Get user successfully',
            'data': {
               'user': user,
               'addresses': addresses,
               'payment_methods': payment_methods,
               'orders': orders,
            }
         }, status=status.HTTP_200_OK)
      
      except UserClientModel.DoesNotExist:
         return Response({
            'message': 'Usuario no encontrado'
         }, status=status.HTTP_404_NOT_FOUND)
      
      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserClient(UpdateAPIView):
   queryset = UserClientModel.objects.all()
   serializer_class = UserClientSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación
   def update(self, request, *args, **kwargs):
      try:
         response = super().update(request, *args, **kwargs)

         return Response({
            'message': 'Usuario actualizado correctamente',
            'data': response.data,
         }, status=status.HTTP_200_OK)
         
      except UserClientModel.DoesNotExist as e:
         return Response({
            'message': 'Usuario no encontrado',
         }, status=status.HTTP_404_NOT_FOUND)
      
      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

class UpdateUserAddress(UpdateAPIView):
   queryset = UserAddressModel.objects.all()
   serializer_class = UserAddressSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación

   def update(self, request, *args, **kwargs):
      try:
         response = super().update(request, *args, **kwargs)

         return Response({
            'message': 'Dirección actualizada correctamente',
            'data': response.data,
         }, status=status.HTTP_200_OK)

      except UserAddressModel.DoesNotExist as e:
         return Response({
            'message': 'Usuario no encontrado',
            'error': str(e)
         }, status=status.HTTP_404_NOT_FOUND)
        
      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUserAddressView(ListAPIView):
   queryset = UserAddressModel.objects.all()
   serializer_class = UserAddressSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación

   def list(self, request, *args, **kwargs):
      try:
         token = request.headers.get('Authorization', None)
         if not token:
            return Response({
               'message': 'se requiere Token de usuario'
            }, status=status.HTTP_401_UNAUTHORIZED)
         
         # Decodificar token
         token_user = decode_jwt_token(token)

         # Extraer datos del token
         user_id = token_user.get('user_id', None)

         user_address = self.queryset.get(user_client_id=user_id)
         
         return Response({
            'message': 'Get user address successfully',
            'data': user_address
         }, status=status.HTTP_200_OK)

      except UserAddressModel.DoesNotExist:
         return Response({
            'message': 'El usuario no cuenta con los datos de direccion'
         }, status=status.HTTP_404_NOT_FOUND)

      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


      
class GetUserIdentificationView(ListAPIView):
   queryset = UserClientModel.objects.all()
   serializer_class = UserClientSerializer
   permission_classes = [IsAuthenticated]  # Para la autenticación

   def get(self, request, *args, **kwargs):
      try:
         token = request.headers.get('Authorization', None)
         if not token:
            return Response({
               'message': 'se requiere Token de usuario'
            }, status=status.HTTP_401_UNAUTHORIZED)
         
         # Decodificar token
         token_user = decode_jwt_token(token)
         user_id = token_user.get('user_id')
         email = token_user.get('email')

         user_client = self.queryset.get(id=user_id, email=email)
         
         return Response({
            'message': 'Get user client successfully',
            'data': user_client
         }, status=status.HTTP_200_OK)
      
      except UserClientModel.DoesNotExist:
         return Response({
            'message': 'Usuario no encontrado'
         }, status=status.HTTP_404_NOT_FOUND)
      
      except Exception as e:
         return Response({
            'message': 'Ocurrió un error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
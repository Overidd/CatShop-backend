from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from catshop.permission import IsAdmin

from rest_framework.generics import (
   UpdateAPIView,
   CreateAPIView,
   ListAPIView,
   DestroyAPIView,
)

from .models import (
   OffersModel,
   StoreModel
)

from .serializer import (
   OffersSerializer,
   StoreSerializer
)

from rest_framework.response import Response
from rest_framework import status, serializers

class StoreGetAllView(ListAPIView):
   queryset = StoreModel.objects.all()
   serializer_class = StoreSerializer

   def list(self, request, *args, **kwargs):
      try:
         response = super().list(request, *args, **kwargs)
         return Response({
            'message': 'Listado de tiendas',
            'data': response.data,
         }, status=status.HTTP_200_OK)
      
      except StoreModel.DoesNotExist as e:
         return Response({
            'message': 'Tienda no encontrada',
         }, status=status.HTTP_404_NOT_FOUND)
      
   
class StoreCreateView(CreateAPIView):
   queryset = StoreModel.objects.all()
   serializer_class = StoreSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 

   def create(self, request, *args, **kwargs):
      response = super().create(request, *args, **kwargs)
      return Response({
         'message': 'Nombre de tienda creada',
         'data': response.data,
      }, status=status.HTTP_201_CREATED)
   
      
class StoreUpdateView(UpdateAPIView):
   queryset = StoreModel.objects.all()
   serializer_class = StoreSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 

   def update(self, request, *args, **kwargs):
      try:
         response = super().update(request, *args, **kwargs)
         return Response({
            'message': 'Tienda actualizada',
            'data': response.data,
         }, status=status.HTTP_200_OK)
      
      except StoreModel.DoesNotExist as e:
         return Response({
            'message': 'Tienda no encontrada',
         }, status=status.HTTP_404_NOT_FOUND)
      
class StoreDeleteView(DestroyAPIView):
   queryset = StoreModel.objects.all()
   serializer_class = StoreSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 

   def destroy(self, request, *args, **kwargs):
      try:
         response = super().destroy(request, *args, **kwargs)
         return Response({
            'message': 'Tienda eliminada',
         }, status=status.HTTP_204_NO_CONTENT)
      except StoreModel.DoesNotExist as e:
         return Response({
            'message': 'Tienda no encontrada',
         }, status=status.HTTP_404_NOT_FOUND)
         

class OffersGetAllView(ListAPIView):
   queryset = OffersModel.objects.all()
   serializer_class = OffersSerializer

   def list(self, request, *args, **kwargs):
      try:
         response = super().list(request, *args, **kwargs)
         return Response({
            'message': 'Listado de ofertas',
            'data': response.data,
         }, status=status.HTTP_200_OK)
      
      except OffersModel.DoesNotExist as e:
         return Response({
            'message': 'Oferta no encontrada',
         }, status=status.HTTP_404_NOT_FOUND)
      

class OffersCreateView(CreateAPIView):
   queryset = OffersModel.objects.all()
   serializer_class = OffersSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 
   
   def create(self, request, *args, **kwargs):
      response = super().create(request, *args, **kwargs)
      return Response({
         'message': 'Oferta creada',
         'data': response.data,
      }, status=status.HTTP_201_CREATED)
   
      
class OffersUpdateView(UpdateAPIView):
   queryset = OffersModel.objects.all()
   serializer_class = OffersSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 
   
   def update(self, request, *args, **kwargs):
      try:
         response =  super().update(request, *args, **kwargs)

         return Response({
            'message': 'Oferta actualizada',
            'data': response.data,
         }, status=status.HTTP_200_OK)

      except OffersModel.DoesNotExist as e:
         return Response({
            'message': 'Oferta no encontrada',
         }, status=status.HTTP_404_NOT_FOUND)
      
class OffersDesactivate(DestroyAPIView):
   queryset = OffersModel.objects.all()
   serializer_class = OffersSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 

   def destroy(self, request, *args, **kwargs):
      try:
         offer = self.queryset.destroy(pk=kwargs.get('pk'))

         if offer.is_active:
            offer.is_active = False
            offer.save()
            return Response({
               'message': 'La oferta no se ha desactivado',
            }, status=status.HTTP_400_BAD_REQUEST)

         if not offer.is_active:
            offer.is_active = True
            offer.save()

            return Response({
               'message': 'La oferta se ha desactivado',
            }, status=status.HTTP_200_OK)
      
      except OffersModel.DoesNotExist as e:
         return Response({
            'message': 'Oferta no encontrada',
         }, status=status.HTTP_404_NOT_FOUND)
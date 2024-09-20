from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

import cloudinary
import cloudinary.uploader

from catshop.permission import IsAdmin

from rest_framework.generics import (
   CreateAPIView,
   UpdateAPIView,
   ListAPIView,  
)

from .models import (
   ProductModel,
   ProductDetailModel,
   ProductCategoryModel,
   ProductImageModel,
   ProductBrandModel,
)

from .serializer import (
   ProductSerializer,
   CreateProductSerializer,
   UpdateProductSerializer,
   ProductListSerializer,
   ProductDetailSerializer,
   ByIdproductSerializer,
   ProductImageSerializer,
   VerifyQuantitySerializer,
   ProductCategorySerializer,
   ProductBrandSerializer
)

from hashids import Hashids
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from catshop.response import (
   IsActiveResponse,
   VerifyQuantityResponse,
   BAD_REQUEST,
   ERROR_SERVER,
   NOT_FOUND,
)

from requests.exceptions import ConnectionError

hashids = Hashids(salt=settings.SALT_HASHIDS, min_length=6)

class CreateProductView(CreateAPIView):
   serializer_class = CreateProductSerializer
   # permission_classes = [IsAuthenticated,IsAdmin] 
   
   @swagger_auto_schema(
      request_body=CreateProductSerializer,
      responses={
         201: CreateProductSerializer,
         400: BAD_REQUEST,
         500: ERROR_SERVER,
      }
    )
   @transaction.atomic
   def post(self, request, *args, **kwargs):
      try:
         serializer = self.serializer_class(data=request.data)
         serializer.is_valid(raise_exception=True) # Para ValidationError 

         validated_data = serializer.validated_data
         # Manejar datos Para el model ProductModel
         name = validated_data.get('name')
         price = validated_data.get('price')
         discount = validated_data.get('discount', 0)
         description = validated_data.get('description')
         stock = validated_data.get('stock')
         category_id = validated_data.get('category_id')
         brand_id = validated_data.get('brand_id')

         # Manejar datos de detalle para el model ProductDetalsModel
         color = validated_data.get('color')
         denifit = validated_data.get('denifit')
         dimension = validated_data.get('dimension')
         size = validated_data.get('size')
         characteristics = validated_data.get('characteristics')
         extra = validated_data.get('extra')

         # Manejar de imágenes
         image1 = validated_data.get('image1', None)
         image2 = validated_data.get('image2', None)
         image3 = validated_data.get('image3', None)
         
         is_category= ProductCategoryModel.objects.filter(id=category_id).first()
         if not is_category:
            return Response({
                'message': 'Categoría no existente',
             }, status=status.HTTP_404_NOT_FOUND)
         
         is_brand = ProductBrandModel.objects.filter(id=brand_id).first()
         if not is_brand:
            return Response({
                'message': 'Marca no existente',
             }, status=status.HTTP_404_NOT_FOUND)
         
         # Crear el producto
         new_product = ProductModel.objects.create(
            name=name,
            price=price,
            discount=discount,
            description=description,
            stock=stock,
            category_id=category_id,
            brand_id=brand_id,
         )
         code = hashids.encode(new_product.id)
         new_product.code = code
         new_product.save()

         # Crear los detalles del producto
         ProductDetailModel.objects.create(
            color=color,
            denifit=denifit,
            dimension=dimension,
            size=size,
            characteristics=characteristics,
            extra=extra,
            product=new_product,
         )

         # Subir imágenes a Cloudinary
         if image1:
            ProductImageModel.objects.create(
               image=image1,
               default=True,
               product=new_product,
            )
         
         if image2:
            ProductImageModel.objects.create(
               image=image2,
               default=False,
               product=new_product,
            )
         
         if image2:
            ProductImageModel.objects.create(
               image=image2,
               default=False,
               product=new_product,
            )

         return Response({
            'message': 'Producto creado exitosamente',
            'data': serializer.data
         },status=status.HTTP_201_CREATED)
         
      except serializers.ValidationError as e:
            # transaction.rollback() 
         return Response({
             "message": "Datos inválidos",
             "error": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)
         
      except Exception as e:
         print(e)
            # transaction.rollback() 
         return Response({
            'message': 'Ocurrió un error inesperado',
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
class UpdateProductView(UpdateAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = UpdateProductSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 
   
   def update(self, request, *args, **kwargs):
      try:
         id_product = kwargs.get('pk')
         if not id_product:
             return Response({
               'message': 'Envia el id del producto',
            }, status=status.HTTP_404_NOT_FOUND)

         serializer = self.serializer_class(data=request.data)
         serializer.is_valid(raise_exception=True) 

         validated_data = serializer.validated_data

         product_data = {
            'name': validated_data.get('name'),
            'price': validated_data.get('price'),
            'discount': validated_data.get('discount'),
            'description': validated_data.get('description'),
            'stock': validated_data.get('stock'),
            'category_id': validated_data.get('category_id'),
            'brand_id': validated_data.get('brand_id'),
         }

         detail_data = {
            'color': validated_data.get('color'),
            'denifit': validated_data.get('denifit'),
            'dimension': validated_data.get('dimension'),
            'size': validated_data.get('size'),
            'characteristics': validated_data.get('characteristics'),
            'extra': validated_data.get('extra'),
         }

         images = validated_data.get('images', [])
         ids_destroy_images = validated_data.get('ids_destroy_images', [])
         default_image_id = validated_data.get('default_image_id', None)


         product = ProductModel.objects.filter(id=id_product, status=True).first()
         if not product:
             return Response({
                'message': 'Producto no encontrado o no está deshabilitado',
             }, status=status.HTTP_404_NOT_FOUND)
             
         for clave, value in product_data.items():
            if value is not None:
               setattr(product, clave, value)
         product.save()

         # Actualizar los detalles del producto si existen
         if hasattr(product, 'product_detail'):
            product_detail = product.product_detail
            for clave, value in detail_data.items():
               if value is not None:
                  setattr(product_detail, clave, value)
            product_detail.save()

         # Subir nuevas imágenes
         for image in images:
           ProductImageModel.objects.create(
               image=image,
               product=product,
           )

         # Eliminar imágenes según ids
         for id_image in ids_destroy_images:
            try:
               product_image = ProductImageModel.objects.get(id=id_image, product=product)
               public_id = product_image.image.public_id
               cloudinary.uploader.destroy(public_id)
               product_image.delete()
            except ProductImageModel.DoesNotExist:
               continue

         # Actualizar la imagen predeterminada
         if default_image_id:
            ProductImageModel.objects.filter(product=product).update(default=False)
            default_image = ProductImageModel.objects.filter(id=default_image_id, product=product).first()
            if default_image:
               default_image.default = True
               default_image.save()

         return Response({
             'message': 'Producto actualizado exitosamente',
             'data': serializer.data
         }, status=status.HTTP_200_OK)

      except ProductModel.DoesNotExist:
         return Response({
            "message": "Producto no encontrado",
            "error": "error"
         }, status=status.HTTP_404_NOT_FOUND)
      except serializers.ValidationError as e:
         transaction.rollback() 
         return Response({
            "message": "Datos inválidos",
            "errors": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
         return Response({
            'message': 'Error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IsActiveProduc(ListAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = IsActiveResponse
   permission_classes = [IsAuthenticated,IsAdmin] 

   def list(self, request, *args, **kwargs):
      id_product = kwargs.get('pk')
      if not id_product:
         return Response({
            'message': 'Envia el id del producto',
         }, status=status.HTTP_400_BAD_REQUEST)
      try:
      
         product = self.queryset.get(id=id_product)

         if product.status:
            product.status = False
            product.save()
            return Response({
              'message': 'El producto está deshabilitado',
              'data': False,
            }, status=status.HTTP_200_OK)
         
         product.status = True
         product.save()
         return Response({
            'message': 'El producto esta habilitado',
            'data': True,
         }, status=status.HTTP_404_NOT_FOUND)

      except ProductModel.DoesNotExist:
         return Response({
            'message': 'Producto no encontrado',
         }, status=status.HTTP_404_NOT_FOUND)

      except Exception as e:
         return Response({
            'message': 'Error inesperado',
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomPageNumberPagination(PageNumberPagination):
   page_size = 20
   page_size_query_param = 'page_size'
   max_page_size = 100

class ProductFilter(django_filters.FilterSet):
   min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte') #  mayor o igual a (gte)
   max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')  #  menor o igual a (lte) 
   discount = django_filters.NumberFilter(field_name="discount", lookup_expr='lte')
   category = django_filters.CharFilter(field_name="category__name", lookup_expr='icontains')
   brand = django_filters.CharFilter(field_name="brand__name", lookup_expr='icontains')

   #Busqueda por el nombre del producto 
   search = django_filters.CharFilter(field_name="name", lookup_expr='icontains')  

   class Meta:
      model =  ProductModel
      fields = ['price', 'category', 'brand', 'discount']

class ProductListAllView(ListAPIView):
   queryset = ProductModel.objects.filter(status=True)
   serializer_class = ProductListSerializer
   filter_backends = [DjangoFilterBackend]
   filterset_class = ProductFilter
   pagination_class = CustomPageNumberPagination  # Aplicar la paginación personalizada
   # search_fields = ['name']  # Campos que se pueden buscar /products/?search=laptop

   def list(self, request, *args, **kwargs):
      response = super().list(request, *args, **kwargs)

      try:
         return Response({
            'message': 'Get all products successfully',
            'data': response.data
            })

      except Exception as e:
         return Response({
            'message': 'Ocurrio un error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetByIdProduct(ListAPIView):
   queryset = ProductModel.objects.filter(status=True)
   serializer_class = ByIdproductSerializer
   def list(self, request, *args, **kwargs):
      id_product = kwargs.get('pk')
      if not id_product:
         return Response({
            'message': 'Envia el id del producto',
         }, status=status.HTTP_400_BAD_REQUEST)
      
      try:
         product = self.queryset.get(id=id_product)
         product_details = {}
         product_images = []
         if hasattr(product, 'product_detail'):
            product_details_model = product.product_detail
            product_details = ProductDetailSerializer(product_details_model).data
         
         if hasattr(product, 'product_image'):
            product_images_model = product.product_image.all()
            product_images = ProductImageSerializer(product_images_model, many=True).data
         
         return Response({
            'message': 'get product successfully',
            'data': {
               'product': ProductSerializer(product).data,
               'details': product_details,
               'images': product_images,
            }
         })

      except ProductModel.DoesNotExist:
         return Response({
            'message': 'Producto no encontrado',
         }, status=status.HTTP_404_NOT_FOUND)
       
      except Exception as e:
         return Response({
            'message': 'Error inesperado',
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyQuantity(CreateAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = VerifyQuantitySerializer

   @swagger_auto_schema(
      request_body=VerifyQuantitySerializer,
      responses={
         200: VerifyQuantityResponse,
         400: VerifyQuantityResponse,
         404: NOT_FOUND,
         500: ERROR_SERVER,
      }
    )
   def post(self, request, *args, **kwargs):
      try:
         serializer = self.serializer_class(data=request.data)
         serializer.is_valid(raise_exception=True)
         validated_data = serializer.validated_data

         product_id = validated_data.get('product_id')
         quantity = validated_data.get('quantity')

         product = ProductModel.objects.filter(id=product_id, status=True).first()
         if not product:
            return Response({
                'message': 'Producto no encontrado o no está habilitado',
             }, status=status.HTTP_404_NOT_FOUND)
         
         if product.stock >= quantity:
            return Response({
               'message': 'La cantidad es válida',
               'data': True,
             }, status=status.HTTP_200_OK)
         if product.stock < quantity:
            return Response({
               'message': 'La cantidad no es válida, no hay stock suficiente',
               'data': False,
             }, status=status.HTTP_400_BAD_REQUEST)

      except serializers.ValidationError as e:
         return Response({
            "message": "Datos inválidos",
            "error": e.detail 
         }, status=status.HTTP_400_BAD_REQUEST)
      
      except Exception as e:
         return Response({
            'message': 'Error inesperado',
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductCategoryGelAllView(ListAPIView):
   queryset = ProductCategoryModel.objects.all()
   serializer_class = ProductCategorySerializer
   def list(self, request, *args, **kwargs):
      try:
         response = super().list(request, *args, **kwargs)
      
         return Response({
            'message': 'Listado de categorias',
            'data': response.data
         })
      
      except ProductCategoryModel.DoesNotExist as e:
         return Response({
            'message': 'Categoría no encontrada'
         }, status=status.HTTP_404_NOT_FOUND)

class ProductCategoryCreate(CreateAPIView):
   queryset = ProductCategoryModel.objects.all()
   serializer_class = ProductCategorySerializer
   # permission_classes = [IsAuthenticated,IsAdmin] 

   def create(self, request, *args, **kwargs):
      response = super().create(request, *args, **kwargs)
      
      return Response({
         'message': 'Categoria creado exitosamente',
         'data': response.data
      })

class ProductCategoryUpdateView(UpdateAPIView):
   queryset = ProductCategoryModel.objects.all()
   serializer_class = ProductCategorySerializer
   permission_classes = [IsAuthenticated,IsAdmin] 

   def update(self, request, *args, **kwargs):
      try:
          response = super().update(request, *args, **kwargs)
          return Response({
              'message': 'Categoria actualizado exitosamente',
              'data': response.data
          }, status=status.HTTP_200_OK)
      
      except ProductCategoryModel.DoesNotExist:
          return Response({
              'message': 'Categoria no encontrado'
          }, status=status.HTTP_404_NOT_FOUND)


class ProductBrandGelAllView(ListAPIView):
   queryset = ProductBrandModel.objects.all()
   serializer_class = ProductBrandSerializer

   def list(self, request, *args, **kwargs):
      try:
         response = super().list(request, *args, **kwargs)
      
         return Response({
            'message': 'Listado de marcas exitosamente',
            'data': response.data
         })
      except ProductBrandModel.DoesNotExist as e:
          return Response({
             'message': 'Marca no encontrada'
          }, status=status.HTTP_404_NOT_FOUND)
      
   
class ProductBrandCreateView(CreateAPIView):
   queryset = ProductBrandModel.objects.all()
   serializer_class = ProductBrandSerializer
   # permission_classes = [IsAuthenticated,IsAdmin] 

   def create(self, request, *args, **kwargs):
      response = super().create(request, *args, **kwargs)
      
      return Response({
         'message': 'Marca creado exitosamente',
         'data': response.data
      })
   
class ProductBrandUpdateView(UpdateAPIView):
   queryset = ProductBrandModel.objects.all()
   serializer_class = ProductBrandSerializer
   permission_classes = [IsAuthenticated,IsAdmin] 
   
   def update(self, request, *args, **kwargs):
      try:
          response = super().update(request, *args, **kwargs)
          return Response({
              'message': 'Marca actualizado exitosamente',
              'data': response.data
          }, status=status.HTTP_200_OK)
      
      except ProductCategoryModel.DoesNotExist:
          return Response({
              'message': 'Marca no encontrado'
          }, status=status.HTTP_404_NOT_FOUND)
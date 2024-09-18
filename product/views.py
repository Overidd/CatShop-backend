from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

import cloudinary
import cloudinary.uploader

from rest_framework.generics import (
   ListCreateAPIView,
   CreateAPIView,
   UpdateAPIView,
   ListAPIView,  
)

from .models import (
   ProductModel,
   ProductDetailModel,
   ProductCategoryModel,
   ProductImageModel,
)

from .serializer import (
   ProductSerializer,
   CreateProductSerializer,
   UpdateProductSerializer,
   ProductListSerializer,
   ProductDetailSerializer,
   ByIdproductSerializer,
   ProductImageSerializer,
   VerifyQuantitySerializer
)

from hashids import Hashids
hashids = Hashids(salt="sdf78Pxq34lZsada", min_length=6)

# Create your views here.
class ProductView(ListCreateAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = ProductSerializer
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
   # search_fields = ['name']  # Campos que se pueden buscar /products/?search=laptop
   pagination_class = CustomPageNumberPagination  # Aplicar la paginación personalizada

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


class CreateProductView(CreateAPIView):
   serializer_class = CreateProductSerializer

   @transaction.atomic
   def post(self, request, *args, **kwargs):
         try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True) # Para ValidationError 

            validated_data = serializer.validated_data
            print(validated_data)
            # Manejar datos Para el model ProductModel
            name = validated_data.get('name')
            price = validated_data.get('price')
            discount = validated_data.get('discount', 0)
            description = validated_data.get('description')
            stock = validated_data.get('stock')
            category_id = validated_data.get('category_id')
            print(category_id, 'category_id')
            brand_id = validated_data.get('brand_id')

            # Manejar datos de detalle para el model ProductDetalsModel
            color = validated_data.get('color')
            denifit = validated_data.get('denifit')
            dimension = validated_data.get('dimension')
            size = validated_data.get('size')
            characteristics = validated_data.get('characteristics')
            extra = validated_data.get('extra')

            # Manejar de imágenes
            images = validated_data.get('images', [])

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
            image_products = []
            defaul = True
            for image in images:
               is_default = defaul
               defaul = False

               new_product_image = ProductImageModel.objects.create(
                  image=image,
                  default=is_default,
                  product=new_product,
               )
               image_products.append(new_product_image.image.url)

            return Response({
               'message': 'Producto creado exitosamente',
               'data': serializer.data
               # 'data': {
               #    'product': serializer.data,
               #    'images': image_products
               # }
            },status=status.HTTP_201_CREATED)
         
         except serializers.ValidationError as e:
            # transaction.rollback() 
            return Response({
                "message": "Datos inválidos",
                "errors": e.detail 
            }, status=status.HTTP_400_BAD_REQUEST)
         
         except Exception as e:
            # transaction.rollback() 
            return Response({
               'message': 'Ocurrió un error inesperado',
               'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
class UpdateProductView(UpdateAPIView):
    queryset = ProductModel.objects.all()
    serializer_class = UpdateProductSerializer

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


            product = ProductModel.objects.get(id=id_product, status=True)
            if not product:
                return Response({
                   'message': 'Producto no encontrado o no está habilitado',
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
            })

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
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IsActiveProduc(ListAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = ProductSerializer

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
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyQuantity(ListAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = ProductSerializer


class ProductCategoryView(ListCreateAPIView):
   queryset = ProductCategoryModel.objects.all()
   serializer_class = VerifyQuantitySerializer

   def list(self, request, *args, **kwargs):
      try:
         pass
      except Exception as e:
         return Response({
            'message': 'Error inesperado',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      return


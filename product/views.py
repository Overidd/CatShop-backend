from rest_framework.response import Response
from rest_framework import status, serializers
from django.db import transaction
from rest_framework.views import APIView
import cloudinary
import cloudinary.uploader

from rest_framework.generics import (
   ListCreateAPIView,
   CreateAPIView,
   UpdateAPIView,
)

from .models import (
   ProductModel,
   ProductDetailModel,
   ProductCategoryModel,
   ProductImageModel,
)

from .serializer import (
   ProductCategorySerializer,
   ProductSerializer,
   CreateProductSerializer,
   UpdateProductSerializer,
)

from hashids import Hashids
hashids = Hashids(salt="sdf78Pxq34lZsada", min_length=6)

# Create your views here.
class ProductView(ListCreateAPIView):
   queryset = ProductModel.objects.all()
   serializer_class = ProductSerializer
   

class CreateProductView(CreateAPIView):
   serializer_class = CreateProductSerializer

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
            transaction.rollback() 
            return Response({
                "message": "Datos inválidos",
                "errors": e.detail 
            }, status=status.HTTP_400_BAD_REQUEST)
         
         except Exception as e:
            transaction.rollback() 
            return Response({
               'message': 'Ocurrió un error inesperado',
               'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
class UpdateProductView(UpdateAPIView):
   serializer_class = UpdateProductSerializer

   def update(self, request, *args, **kwargs):
      try:
         id_product = kwargs.get('pk')

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

         # Nuevas imágenes
         images = validated_data.get('images', [])

         # Ids para borrar las imagenes
         ids_destroy_images = validated_data.get('ids_destroy_images', [])

         # Id para actualizar una imagen como defaul
         default_image_id = validated_data.get('default_image_id', None)
         
         # Buscar el producto y actualizar
         product = ProductModel.objects.get(id=id_product)
         product.name = name
         product.price = price
         product.discount = discount
         product.description = description
         product.stock = stock
         product.category_id = category_id
         product.brand_id = brand_id
         product.save()

         # Actualizar los detalles del producto
         product_details = product.product_detail
         product_details.color = color
         product_details.denifit = denifit
         product_details.dimension = dimension
         product_details.size = size
         product_details.characteristics = characteristics
         product_details.extra = extra
         product_details.save()

         # Subir imágenes a Cloudinary
         image_products = []
         for image in images:
            new_product_image = ProductImageModel.objects.create(
               image=image,
               product=product,
            )
            image_products.append(new_product_image.image.url)

         # Borrar imagenes de cloudinary segun los id y del model
         for id_image in ids_destroy_images:
            product_image = ProductImageModel.objects.filter(id=id_image, product=product)
            public_id = product_image.image.public_id
            # Eliminar la imagen de cloudinary con el public_id
            cloudinary.uploader.destroy(public_id)
            image.delete()

         # Actualizar el campo defaul de las imagenes
         if default_image_id:
            images = ProductImageModel.objects.filter(product=product)
            
            if images.exists():
               images.update(default=False)

               image_default = images.filter(id=default_image_id).first()
               if image_default:
                  image_default.default = True
                  image_default.save()

         return Response({
            'message': 'Producto actualizado exitosamente',
             'data': serializer.data
             # 'data': {
             #    'product': serializer.data,
             #    'images': image_products
             # }
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
            'message': 'Error al crear la categoría',
            'error': str(e)
         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      return super().post(request, *args, **kwargs)


class ProductCategoryView(ListCreateAPIView):
   queryset = ProductCategoryModel.objects.all()
   serializer_class = ProductCategorySerializer
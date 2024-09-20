from django.db import models
from cloudinary.models import CloudinaryField

class ProductCategoryModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=100, null=False)
   image = CloudinaryField('image', folder='category/', null=True)

   class Meta:
      db_table = 'product_category'
      verbose_name =  'Categoria'
      verbose_name_plural = 'Categorias'
      
   def __str__(self):
      return self.name

class ProductBrandModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=100)

   class Meta:
      db_table = 'product_brand'
      verbose_name = 'Marca'
      verbose_name_plural = 'Marcas'
   
   def __str__(self):
      return self.name

#* ---.
class ProductModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=100)
   price = models.FloatField(default=0)
   discount = models.IntegerField(null=True, default=0) # Descuento pero valor porcentaje
   description = models.TextField(null=True)
   code = models.CharField(max_length=100, null=True,unique=True)
   status = models.BooleanField(default=True)
   stock = models.IntegerField(null=False, default=1)
   category = models.ForeignKey(ProductCategoryModel, on_delete=models.CASCADE, related_name='product_category')
   brand = models.ForeignKey(ProductBrandModel, null=True,on_delete=models.SET_NULL, related_name='product_brand') 
   
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)   

   class Meta:
      db_table = 'product'
      verbose_name = 'Producto'
      verbose_name_plural = 'Productos'

   def __str__(self):
      return self.name
   
  
class ProductDetailModel(models.Model):
   id = models.AutoField(primary_key=True)
   color = models.CharField(max_length=100, null=True)
   denifit = models.CharField(max_length=200,null=True)
   dimension = models.CharField(max_length=100, null=True)
   size = models.CharField(max_length=20, null=True)
   characteristics = models.TextField(null=True)
   extra = models.CharField(max_length=200, null=True)
   product = models.OneToOneField(ProductModel, on_delete=models.CASCADE, related_name='product_detail')

   class Meta:
      db_table = 'product_detail'
      verbose_name = 'Detalle del producto'
      verbose_name_plural = 'Detalles del producto'
   
   def __str__(self):
      return self.product.name

class ProductImageModel(models.Model):
   id = models.AutoField(primary_key=True)
   image = CloudinaryField('image', folder='product/')
   default = models.BooleanField(null=True, default=False)
   product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='product_image')

   class Meta:
      db_table = 'product_image'
      verbose_name = 'Imagen del producto'
      verbose_name_plural = 'Imágenes del producto'


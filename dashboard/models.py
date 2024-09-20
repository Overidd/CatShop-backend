from django.db import models
from cloudinary.models import CloudinaryField
from product.models import ProductCategoryModel

class OffersModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=100)
   description = models.TextField(null=True)
   discount = models.FloatField(default=0, null=True)
   status = models.BooleanField(default=True)
   image = CloudinaryField('image', folder='offers')
   category = models.ForeignKey(ProductCategoryModel, null=True, on_delete=models.SET_NULL, related_name='offers_category')
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      db_table = 'offers'
      verbose_name = 'oferta'
      verbose_name_plural = 'ofertas'

   def __str__(self):
      return self.name


class StoreModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=200)
   schedules = models.TimeField(null=True)
   status = models.BooleanField(default=True, null=True)
   address = models.CharField(max_length=100)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      db_table = 'store'
      verbose_name = 'tienda'
      verbose_name_plural = 'tiendas'

   def __str__(self):
      return self.name
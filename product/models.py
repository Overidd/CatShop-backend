from django.db import models
from cloudinary.models import CloudinaryField

class ProductCategoryModel(models.Model):
   name = models.CharField(max_length=250, null=False)
   image = CloudinaryField('image', folder='category')

   class Meta:
      db_table = 'product_category'

from hashids import Hashids
hashids = Hashids(salt="sdf78Pxq34lZsada", min_length=6)
# Create your models here.
class ProductModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=250, null=False)
   description = models.TextField(null=False)
   price = models.FloatField(null=False)
   discount = models.FloatField(null=True, default=0)
   code = models.CharField(max_length=100, null=True)
   status = models.BooleanField(default=True)
   stock = models.IntegerField(null=False, default=1)
   category = models.ForeignKey(ProductCategoryModel, on_delete=models.CASCADE) 
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   
   def save(self, *args, **kwargs):
      if not self.code:
         self.code = 'prt-'+hashids.encode(self.id)
      super().save(*args, **kwargs)
    

   class Meta:
      db_table = 'product'


from django.db import models
from cloudinary.models import CloudinaryField

class ProductCategory(models.Model):
   name = models.CharField(max_length=250, null=False)
   image = CloudinaryField('image', folder='category')

   class Meta:
      db_table = 'product_category'


# Create your models here.
class ProductModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=250, null=False)
   description = models.TextField(null=False)
   price = models.DecimalField(max_digits=4, decimal_places=2, null=False)
   discount = models.DecimalField(max_digits=4,decimal_places=2, null=True, default=0)
   code = models.CharField(max_length=100, null=True)
   status = models.BooleanField(default=True)
   stock = models.IntegerField(null=False, default=1)
   
   category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE) 
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      db_table = 'product'
 

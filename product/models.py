from django.db import models

class ProductCategory(models.Model):
   pass
   name = models.CharField(max_length=250, null=False)
   image = models.ImageField(upload_to='category/')

# Create your models here.
class ProductModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=250, null=False)
   description = models.TextField(null=False)
   price = models.DecimalField(decimal_places=2,null=False)
   discount = models.DecimalField(decimal_places=2, null=True, default=0)
   code = models.CharField(max_length=100, null=True)
   status = models.BooleanField(default=True)
   stock = models.IntegerField(null=False, default=1)
   
   category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE) 
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)


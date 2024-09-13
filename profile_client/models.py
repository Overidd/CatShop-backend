from django.db import models
from cloudinary.models import CloudinaryField
from purchases.models import OrderModel
from product.models import ProductModel

class UserClientModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=200)
   image = CloudinaryField('image', folder='user_client/')
   last_name = models.CharField(max_length=200, null=True)
   password = models.TextField(blank=False, null=False)
   email = models.EmailField(max_length=254, unique=True)
   code_google = models.CharField(max_length=200, blank=True, null=True)
   document_number = models.CharField(max_length=10, blank=True, null=True)
   ruc = models.CharField(max_length=10, blank=True, null=True)
   verification_code = models.CharField(max_length=6, blank=True, null=True)  # Nuevo campo para el código de verificación
   is_verified = models.BooleanField(default=False)  # Para saber si el usuario ha verificado su cuenta
   status = models.BooleanField(default=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      db_table = 'user_client'


class UserAddressModel(models.Model):
   id = models.AutoField(primary_key=True)
   department = models.CharField(max_length=100)
   province = models.CharField(max_length=100)
   district = models.CharField(max_length=100)
   address = models.CharField(max_length=250, null=True)
   street = models.CharField(max_length=100, null=True)
   street_number = models.CharField(max_length=50,null=True) 
   reference = models.TextField(null=True)
   user_client = models.ForeignKey(UserClientModel, related_name='user_address' ,on_delete=models.CASCADE)

   class Meta:
      db_table = 'user_address'

class UserPaymentMethodModel(models.Model):
   id = models.AutoField(primary_key=True)
   amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
   payment_method = models.CharField(max_length=100)
   patment_date = models.DateTimeField(auto_now_add=True)
   user_client = models.ForeignKey(UserClientModel, related_name='user_payment', null=True,on_delete=models.CASCADE)

   class Meta:
      db_table = 'user_payment_method'

class UserOrderModel(models.Model):
   id = models.AutoField(primary_key=True)
   order = models.OneToOneField(OrderModel, related_name='user_order', on_delete=models.CASCADE)
   user_client = models.ForeignKey(UserClientModel, related_name='user_client', on_delete=models.CASCADE)

   class Meta:
      db_table = 'user_order'
   
   
class UserFavoritesModel(models.Model):
   id = models.AutoField(primary_key=True)
   product = models.ForeignKey(ProductModel, related_name='favorite_product', on_delete=models.CASCADE)
   user_client = models.ForeignKey(UserClientModel, related_name='favorite_user', on_delete=models.CASCADE)
      
   class Meta:
        db_table = 'user_favorite'

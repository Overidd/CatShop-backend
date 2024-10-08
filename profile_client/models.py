from django.db import models
from cloudinary.models import CloudinaryField
from purchases.models import OrderModel
from product.models import ProductModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class RoleModel(models.Model):
    id = models.AutoField(primary_key=True)

    ROLE_NAME_CHOICES = [
        ('CLIENT', 'Cliente'),
        ('ADMIN', 'Administrador'),
    ]

    name = models.CharField(max_length=100, choices=ROLE_NAME_CHOICES, default='CLIENT')

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name

from .manage import UserClientManager

class UserClientModel(AbstractBaseUser, PermissionsMixin):
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

   is_superuser = models.BooleanField(default=False, null=True)
   role = models.ForeignKey(RoleModel, on_delete=models.CASCADE, related_name='users', default=1)
   is_staff = models.BooleanField(default=False, null=True)

   objects = UserClientManager()
   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = []

   class Meta:
      db_table = 'user_client'
      verbose_name = 'usuario'
      verbose_name_plural = 'usuarios'
   
   def __str__(self):
        return self.email

   def has_perm(self, perm, obj=None):
        return self.is_superuser

   def has_module_perms(self, app_label):
        return self.is_superuser


class UserAddressModel(models.Model):
   id = models.AutoField(primary_key=True)
   department = models.CharField(max_length=100)
   province = models.CharField(max_length=100)
   district = models.CharField(max_length=100)
   address = models.CharField(max_length=250, null=True)
   street = models.CharField(max_length=100, null=True)
   street_number = models.CharField(max_length=50,null=True) 
   reference = models.TextField(null=True)
   user_client = models.OneToOneField(UserClientModel, related_name='user_address' ,on_delete=models.CASCADE)

   class Meta:
      db_table = 'user_address'
      verbose_name = 'dirección'
      verbose_name_plural = 'direcciones'

class UserPaymentMethodModel(models.Model):
   id = models.AutoField(primary_key=True)
   amount = models.FloatField(null=True)
   payment_method = models.CharField(max_length=100)
   payment_number = models.CharField(max_length=100, null=True)
   card_type = models.CharField(max_length=100, null=True)
   card_name = models.CharField(max_length=100, null=True)
   country_code = models.CharField(max_length=10, null=True)
   installments = models.IntegerField(null=True)
   payment_date = models.DateTimeField(auto_now_add=True)
   user_client = models.ForeignKey(UserClientModel, related_name='user_payment', null=True,on_delete=models.CASCADE)

   class Meta:
      db_table = 'user_payment_method'
      verbose_name = 'metodo de pago'
      verbose_name_plural ='metodos de pago'

class UserOrderModel(models.Model):
   id = models.AutoField(primary_key=True)
   order = models.OneToOneField(OrderModel, related_name='user_order', on_delete=models.CASCADE)
   user_client = models.ForeignKey(UserClientModel, related_name='user_client', on_delete=models.CASCADE)

   class Meta:
      db_table = 'user_order'
      verbose_name = 'orden user'
      verbose_name_plural = 'ordenes user'
   
   
class UserFavoritesModel(models.Model):
   id = models.AutoField(primary_key=True)
   product = models.ForeignKey(ProductModel, related_name='favorite_product', on_delete=models.CASCADE)
   user_client = models.ForeignKey(UserClientModel, related_name='favorite_user', on_delete=models.CASCADE)
      
   class Meta:
      db_table = 'user_favorite'
      verbose_name = 'producto favorito '
      verbose_name_plural = 'productos favoritos'

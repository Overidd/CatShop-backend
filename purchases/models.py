from typing import Iterable
from django.db import models
from product.models import ProductModel
from django.core.validators import MinValueValidator
from hashids import Hashids

hashids = Hashids(salt="sdf78Pxq34lZsada", min_length=6)

# Create your models here.
class OrderModel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=200, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2 ,null=False)
    total_discount =  models.DecimalField(max_digits=10, decimal_places=2 ,null=True)
    status = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = 'order-'+hashids.encode(self.id)
        super().save(*args, **kwargs)
    
    class Meta:
       db_table = 'order'


# quantity = models.IntegerField(null=False, validators=[MinValueValidator(1)])
class OrderDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(null=False, default=1)
    price_unit = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    name_product =  models.CharField(max_length=200, null=True)
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='order_detail')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='product_order_detail')

   #  def save(self, *args, **kwargs):
   #      self.subtotal = self.quantity * self.price
   #      super(OrderDetail, self).save(*args, **kwargs)
    class Meta:
        db_table = 'order_detail'
        ordering = ['order', 'product']
        verbose_name = 'Order Detail'
        verbose_name_plural = 'Order Details'


class OrderIdentificationModel(models.Model):
   id = models.AutoField(primary_key=True)
   email = models.EmailField(null=False)
   name = models.CharField(max_length=250)
   last_name = models.CharField(max_length=250)
   document_number = models.CharField(max_length=10)
   phone = models.CharField(max_length=10)
   ruc = models.CharField(max_length=10, null=True)
   order = models.OneToOneField(OrderModel, null=True, on_delete=models.SET_NULL, related_name='order_identification')

   class Meta:
      db_table = 'order_identification'

# SET_NULL: Al eliminar el objeto relacionado, en lugar de eliminar el objeto que tiene la clave foránea, se establece la clave foránea en NULL. Esto solo funciona si el campo tiene null=True, ya que de lo contrario no se permitiría almacenar NULL.

class OrderDeliveryModel(models.Model):
    id = models.AutoField(primary_key=True) 
    department = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    street_number = models.CharField(max_length=50) 
    reference = models.TextField(null=True)
    order = models.OneToOneField(OrderModel, null=True, on_delete=models.SET_NULL, related_name='order_delivery')
    
    class Meta:
        db_table = 'order_delivery'

class OrderStoreModel(models.Model):
   id = models.AutoField(primary_key=True)
   store_name = models.CharField(max_length=250)
   order = models.OneToOneField(OrderModel, null=True,on_delete=models.SET_NULL, related_name='order_store')

   class Meta:
       db_table = 'order_store'

class OrderPaymentModel(models.Model):
   id = models.AutoField(primary_key=True)
   amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
   payment_method = models.CharField(max_length=100)
   payment_number = models.CharField(max_length=100, null=True)
   card_type = models.CharField(max_length=100, null=True)
   card_name = models.CharField(max_length=100, null=True)
   country_code = models.CharField(max_length=10, null=True)
   installments = models.IntegerField(null=True)
   payment_data = models.DateTimeField(auto_now_add=True)
   order = models.OneToOneField(OrderModel, null=True,on_delete=models.SET_NULL, related_name='order_payment')

   class Meta:
       db_table = 'order_payment'

class OrderUserTempModel(models.Model):
   id = models.AutoField(primary_key=True)
   email = models.EmailField(max_length=200, null=False)
   order = models.OneToOneField(OrderModel, null=True, on_delete=models.SET_NULL, related_name='order_temp')

   class Meta:
      db_table = 'order_user_temp'
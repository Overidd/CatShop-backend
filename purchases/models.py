from django.db import models
from product.models import ProductModel
from django.core.validators import MinValueValidator

# Create your models here.
class OrderModel(models.Model):
   id = models.AutoField(primary_key=True)
   code = models.CharField(max_length=200, null=False, unique=True)
   total = models.DecimalField(max_digits=10, decimal_places=2 ,null=False)   
   status = models.BooleanField(null=False, default=True)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
       db_table = 'order'

# quantity = models.IntegerField(null=False, validators=[MinValueValidator(1)])
class OrderDetailModel(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(null=False, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=False)
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
   ruc = models.CharField(max_length=10)
   order = models.OneToOneField(OrderModel, null=True, on_delete=models.SET_NULL, related_name='order_identification')

   class Meta:
      db_table = 'order_identification'

# SET_NULL: Al eliminar el objeto relacionado, en lugar de eliminar el objeto que tiene la clave foránea, se establece la clave foránea en NULL. Esto solo funciona si el campo tiene null=True, ya que de lo contrario no se permitiría almacenar NULL.

class OrderDeliveryModel(models.Model):
    id = models.AutoField(primary_key=True) 
    department = models.CharField(max_length=250)
    province = models.CharField(max_length=250)
    district = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    street = models.CharField(max_length=250)
    street_number = models.CharField(max_length=50) 
    reference = models.CharField(max_length=250, null=True)
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
   patment_date = models.DateTimeField(auto_now_add=True)
   order = models.OneToOneField(OrderModel, null=True,on_delete=models.SET_NULL, related_name='order_payment')

   class Meta:
       db_table = 'order_payment'

class OrderUserTempModel(models.Model):
   id = models.AutoField(primary_key=True)
   email = models.EmailField(max_length=200, null=False)
   user = models.OneToOneField(OrderModel, null=True, on_delete=models.SET_NULL, related_name='order_user_temp')

   class Meta:
      db_table = 'order_user_temp'
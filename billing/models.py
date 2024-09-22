from django.db import models

# Create your models here.
# Se guarda la informacion de la facturacion generada
class InvoicePaymentsModel(models.Model):
   id = models.AutoField(primary_key=True)
   name_client = models.TextField(max_length=200, null=True)
   email_client = models.TextField(max_length=200, null=True)
   serie = models.CharField(max_length=4, null=True)
   number = models.IntegerField(null=True)
   link = models.TextField(null=True)
   pdf_link = models.TextField(null=True)
   xml_link = models.TextField(null=True)
   accepted_by_sunat = models.BooleanField(default=False, null=True)
   string_for_qr_code = models.TextField(null=True)

   class Meta:
      db_table = 'invoice_payment'
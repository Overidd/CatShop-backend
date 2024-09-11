from django.db import models
from cloudinary.models import CloudinaryField

class UserClientModel(models.Model):
   id = models.AutoField(primary_key=True)
   name = models.CharField(max_length=200, blank=False)
   last_name = models.CharField(max_length=200, blank=True)
   image = CloudinaryField('image', folder='user_client/')
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

   def __str__(self):
        return f"{self.name} {self.last_name}"

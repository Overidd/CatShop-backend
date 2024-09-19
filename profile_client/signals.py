# myapp/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from  profile_client.models import RoleModel

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
   if sender.name == 'profile_client':  
      roles = [
         {'name': 'CLIENT'},  # Rol para clientes
         {'name': 'ADMIN'},   # Rol para administradores
      ]
      for role in roles:
         RoleModel.objects.get_or_create(name=role['name'])

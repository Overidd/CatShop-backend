from django.db.models.signals import post_migrate
from django.dispatch import receiver
from  profile_client.models import RoleModel
from django.db import transaction

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
   if sender.name == 'profile_client':
      roles = [
          {'name': 'CLIENT'},  # Rol para clientes
          {'name': 'ADMIN'},   # Rol para administradores
      ]
      with transaction.atomic():  # Envolver en transacción atómica
         for role in roles:
            RoleModel.objects.get_or_create(name=role['name'])
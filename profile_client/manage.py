from django.contrib.auth.models import BaseUserManager
from .models import RoleModel

class UserClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email requerido')
        email = self.normalize_email(email)

        # Asigna automáticamente el rol de CLIENTE
        client_role = RoleModel.objects.get(name='CLIENT')
        print(client_role)
        extra_fields.setdefault('role', client_role)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Asigna automáticamente el rol de ADMIN
        admin_role = RoleModel.objects.get(name='ADMIN')
        extra_fields.setdefault('role', admin_role)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


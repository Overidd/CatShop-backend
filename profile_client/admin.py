from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserClientModel, UserAddressModel, UserPaymentMethodModel, UserOrderModel, UserFavoritesModel


class UserAddressInline(admin.StackedInline):
    model = UserAddressModel
    extra = 1  

# Inline para agregar imágenes del producto dentro del formulario de producto
class UserPaymentMethodInline(admin.TabularInline):
    model = UserPaymentMethodModel
    extra = 1  


# Personalización del admin para UserClientModel
@admin.register(UserClientModel)
class UserClientAdmin(UserAdmin):
   # Campos que se mostrarán en la lista de usuarios
   list_display = ('email', 'name', 'last_name', 'is_verified', 'is_staff', 'status')

   search_fields = ('email', 'name', 'last_name', 'document_number', 'ruc')


   list_filter = ('is_verified', 'is_staff', 'status', 'created_at')

   list_editable = ('is_verified', 'is_staff', 'status')
   
   inlines = [UserAddressInline ]
   fieldsets = (
       (None, {'fields': ('email', 'password')}),
       ('Información Personal', {'fields': ('name', 'last_name', 'image', 'document_number', 'ruc')}),
       ('Permisos', {'fields': ('is_verified', 'is_staff', 'is_superuser', 'status', 'role')}),
       ('Fechas Importantes', {'fields': ('last_login', 'created_at', 'updated_at')}),
   )
   # Campos para agregar un nuevo usuario
   add_fieldsets = (
       (None, {
           'classes': ('wide',),
           'fields': ('email', 'image','password1', 'password2', 'is_staff', 'is_superuser', 'status')}
       ),
   )
   # Campos de solo lectura
   readonly_fields = ('created_at', 'updated_at', 'last_login')
   ordering = ('email',)

admin.site.register(UserPaymentMethodModel)
admin.site.register(UserOrderModel)
admin.site.register(UserFavoritesModel)

from django.contrib import admin
from .models import (
   OffersModel,
   StoreModel,
)

# Register your models here.
@admin.register(OffersModel)
class StoreAdmin(admin.ModelAdmin):
   list_display = ('id','name','discount', 'status', 'category')
   search_fields = ('name', 'category')
   list_filter = ('status', 'category')
   fieldsets = (
      ('Nueva oferta', {
         'fields': ('name', 'discount', 'description', 'category', 'image'),
      }),
   )
   readonly_fields = ('created_at', 'updated_at')


# Register your models here.
@admin.register(StoreModel)
class StoreAdmin(admin.ModelAdmin):
   # list_display = ('name','schedules','status', 'address')
   # search_fields = ('address', 'name')
   # list_filter = ('status', 'schedules')
   fieldsets = (
      ('Informacion de la tienda', {
         'fields': ('name','schedules', 'address')
      }),
   )
   readonly_fields = ('created_at', 'updated_at')


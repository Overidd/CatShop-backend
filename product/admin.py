from django.contrib import admin
from .models import ProductCategoryModel,ProductModel


class ProductCategoryAdmin(
   admin.ModelAdmin
):
   list_display = ('id', 'name')
   search_fields = ('name',)
   list_filter = ('name',) 
   
admin.site.register(ProductCategoryModel, ProductCategoryAdmin)
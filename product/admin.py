from django.contrib import admin
from .models import (
    ProductModel, 
    ProductDetailModel, 
    ProductImageModel, 
    ProductCategoryModel, 
    ProductBrandModel
)

# Inline para agregar detalles del producto dentro del formulario de producto
class ProductDetailInline(admin.StackedInline):
    model = ProductDetailModel
    extra = 1  

# Inline para agregar imágenes del producto dentro del formulario de producto
class ProductImageInline(admin.TabularInline):
    model = ProductImageModel
    extra = 1  

# Personalización del admin para ProductModel
@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
   list_display = ('name', 'price', 'discount','stock', 'category', 'brand', 'status')
   search_fields = ('name', 'code')
   list_filter = ('category', 'brand', 'status')
   inlines = [ProductDetailInline, ProductImageInline] 
   fieldsets = (
        ('Información del Producto', {
            'fields': ('name', 'price', 'discount', 'description',  'status', 'stock', 'category', 'brand')
        }),
   )
   readonly_fields = ('created_at', 'updated_at')

# Registro de las categorías y marcas en el admin
@admin.register(ProductCategoryModel)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ProductBrandModel)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

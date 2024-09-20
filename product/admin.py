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
    extra = 1  # Permite agregar un solo formulario de detalles

# Inline para agregar imágenes del producto dentro del formulario de producto
class ProductImageInline(admin.TabularInline):
    model = ProductImageModel
    extra = 1  # Permite agregar múltiples imágenes

# Personalización del admin para ProductModel
@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
   list_display = ('name', 'price', 'stock', 'status', 'category', 'brand')
   search_fields = ('name', 'code')
   list_filter = ('category', 'brand', 'status')
   inlines = [ProductDetailInline, ProductImageInline]  # Incluir los inlines para detalles e imágenes
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

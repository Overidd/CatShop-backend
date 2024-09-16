
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# TODO: Configuracion de swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API de E-commerce",
      default_version='v1',
      description="Documentación de la API para el sistema de e-commerce",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
 
    # Ruta para la documentación swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Rutas de Autenticacion 
    path('api/v1/auth/', include('autentication.urls')),
    path('api/v1/perfil/', include('profile_client.urls')),

    # Rutas de generar order y pasarela de pagos
    path('api/v1/order/', include('payment_gateway.urls')),

    # Rutas para los productos
    path('api/v1/product/', include('product.urls')),
]

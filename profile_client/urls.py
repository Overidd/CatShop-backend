from django.urls import path
from .views import (
   GetallFavoriteView,
   DestroyFavoriteView,
   CreateFavoriteView,
   GetUserByIdView,
   UpdateUserClient,
   UpdateUserAddress,
)

urlpatterns = [
   path('favorite/get_all/<int:pk>/', GetallFavoriteView.as_view()),
   path('favorite/destroy/<int:pk>/', DestroyFavoriteView.as_view()),
   path('favorite/create/', CreateFavoriteView.as_view()),

   # Rutas para el perfil del usuario
   path('user/<int:pk>/', GetUserByIdView.as_view()),
   path('user/update/<int:pk>/', UpdateUserClient.as_view()),
   path('user/address/update/<int:pk>/', UpdateUserAddress.as_view()),
]
from django.urls import path
from .views import (
   GetallFavoriteView,
   DestroyFavoriteView,
   CreateFavoriteView,
   GetUserByIdView,
   UpdateUserClient,
   UpdateUserAddress,
   GetUserAddressView,
   GetUserIdentificationView,
)

urlpatterns = [
   path('favorite/get_all/', GetallFavoriteView.as_view()),
   path('favorite/destroy/', DestroyFavoriteView.as_view()),
   path('favorite/create/', CreateFavoriteView.as_view()),

   # Rutas para el perfil del usuario
   path('user/', GetUserByIdView.as_view()),
   path('user/update/<int:pk>/', UpdateUserClient.as_view()),
   path('user/address/update/<int:pk>/', UpdateUserAddress.as_view()),

   path('address/', GetUserAddressView.as_view()),
   path('identification/', GetUserIdentificationView.as_view()),
]
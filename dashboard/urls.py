from django.urls import path
from .views import (
   StoreGetAllView,
   StoreCreateView,
   StoreUpdateView,
   OffersGetAllView,
   OffersCreateView,
   OffersUpdateView,
)

urlpatterns = [
   path('store/get_all/', StoreGetAllView.as_view()),
   path('store/create/', StoreCreateView.as_view()),
   path('store/update/<int:pk>/', StoreUpdateView.as_view()),

   path('offers/get_all/', OffersGetAllView.as_view()),
   path('offers/create/', OffersCreateView.as_view()),
   path('offers/update/<int:pk>/', OffersUpdateView.as_view()),
]




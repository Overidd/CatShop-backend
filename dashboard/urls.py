from django.urls import path
from .views import (
   StoreGetAllView,
   StoreCreateView,
   StoreUpdateView,
   StoreDeleteView,
   OffersGetAllView,
   OffersCreateView,
   OffersUpdateView,
   OffersDesactivate,
)

urlpatterns = [
   path('store/get_all/', StoreGetAllView.as_view()),
   path('store/create/', StoreCreateView.as_view()),
   path('store/update/<int:pk>/', StoreUpdateView.as_view()),
   path('store/delete/<int:pk>/', StoreDeleteView.as_view()),

   path('offer/get_all/', OffersGetAllView.as_view()),
   path('offer/create/', OffersCreateView.as_view()),
   path('offer/update/<int:pk>/', OffersUpdateView.as_view()),
   path('offer/is_activate/<int:pk>/', OffersDesactivate.as_view()),
]




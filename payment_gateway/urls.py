
from django.urls import path
from .views import (
   RegisterOrderView,
   ProcessPaymentView,
)

# from .views import PaymentView


urlpatterns = [
   path('create/', RegisterOrderView.as_view()),
   # path('payment/', PaymentView.as_view(), name='payment'),
   path('process-payment/', ProcessPaymentView.as_view()),

]

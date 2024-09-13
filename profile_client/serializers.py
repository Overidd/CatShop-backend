from rest_framework.serializers import ModelSerializer

from .models import UserFavoritesModel, UserClientModel, UserAddressModel, OrderModel, UserPaymentMethodModel

class UserClientSerializer(ModelSerializer):
    class Meta:
        model = UserClientModel
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserFavoritesSerializer(ModelSerializer):
    class Meta:
        model = UserFavoritesModel
        fields = '__all__'

        
class UserAddressSerializer(ModelSerializer):
    class Meta:
        model = UserAddressModel
        fields = '__all__'

class UserPaymentMethodSerializer(ModelSerializer):
    class Meta:
        model = UserPaymentMethodModel
        fields = '__all__'

class OrderSerializer(ModelSerializer):
    class Meta:
        model = OrderModel
        fields = '__all__'

class UserDetailSerializer(ModelSerializer):
    user_address = UserAddressSerializer(many=True, read_only=True)
    user_payment = UserPaymentMethodSerializer(many=True, read_only=True)
    user_order = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = UserClientModel
        fields = '__all__'


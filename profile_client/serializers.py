from rest_framework.serializers import ModelSerializer
from .models import UserClientModel

class UserClientSerializer(ModelSerializer):
    class Meta:
        model = UserClientModel
        fields = ['id', 'name', 'last_name', 'email', 'password', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }
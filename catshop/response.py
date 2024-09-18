from rest_framework import serializers

#TODO Serializadores para respuestas
class UserRegisterResponse(serializers.Serializer):
   message = serializers.CharField()

class ResponseTokenUser(serializers.Serializer):
   message = serializers.CharField()
   access_token = serializers.CharField()
   refresh_token = serializers.CharField()


class BAD_REQUEST(serializers.Serializer):
   message = serializers.CharField()
   error = serializers.ListField(
      child=serializers.CharField(),
      required=False,
   )

class NOT_FOUND(serializers.Serializer):
   message = serializers.CharField()

class ERROR_SERVER(serializers.Serializer):
   message = serializers.CharField()

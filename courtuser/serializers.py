""" serializer for rest framework """

from rest_framework import serializers
from .models import CourtUser


class UserSerializer(serializers.ModelSerializer):
  """ serializer for the user """
  # url = serializers.HyperlinkedIdentityField(view_name="courts:user-detail")
  class Meta:
    """ meta class """
    model = CourtUser
    # fields = '__all__'
    fields = ('id', 'username', 'sendEmail', 'is_superuser', 'isSpecial', 'isFreeTrainer')

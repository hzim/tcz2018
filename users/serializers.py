""" serializer for rest framework """

from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """ serializer for the user
    """
    # url = serializers.HyperlinkedIdentityField(view_name="courts:user-detail")
    class Meta:
        model = CustomUser
        # fields = '__all__'
        fields = ('id', 'username', 'is_staff', 'first_name', 'last_name')

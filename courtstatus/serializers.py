""" serializer for rest framework """

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import TczCourtStatus


class TczCourtStatusSerializer(serializers.ModelSerializer):
  """ serializer for the court status
  """
  class Meta:
    """ meta class """
    model = TczCourtStatus
    fields = ('id', 'lock_date', 'lock_comment')

""" serializer for rest framework """

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from courtuser.models import CourtUser
from .models import TczHour
from .views_helper import user_has_reservation


class TczHourSerializer(serializers.ModelSerializer):
  """ serializer for the reserved hour
  """
  class Meta:
    model = TczHour
    fields = '__all__'

  def create(self, validated_data):
    # print('create', validated_data)
    tcz_hour = TczHour(tcz_date=validated_data['tcz_date'],
                       tcz_user=validated_data['tcz_user'],
                       tcz_user_change=validated_data['tcz_user_change'],
                       tcz_court=validated_data['tcz_court'],
                       tcz_hour=validated_data['tcz_hour'],
                       tcz_free=validated_data['tcz_free'],
                       tcz_trainer=validated_data['tcz_trainer'])
    # check the user constraints to make new reservations
    if not validated_data['tcz_free']:
      if user_has_reservation(validated_data['tcz_user']):
        # user already run out of free reservation hours
        return None
    # check if the hour is still free maybe somebody has already reserved it
    try:
      lExistHour = TczHour.objects.get(tcz_date=validated_data['tcz_date'],
                                       tcz_hour=validated_data['tcz_hour'],
                                       tcz_court=validated_data['tcz_court'])
      # hour is already reserved - it cannot be reserved twice
      return None
    except ObjectDoesNotExist:
      # hour is free - so I will save it
      pass
    tcz_hour.save()
    return tcz_hour

  def update(self, instance, validated_data):
    """ update is only allowed for trainer hours """
    lTrainer = CourtUser.objects.get(isFreeTrainer=True)
    #print('update data', validated_data)
    #print('update instance', instance)
    #print("instance=", instance.tcz_user.id, " validated", validated_data['tcz_user'].id)
    if validated_data['tcz_user'].id == lTrainer.id or instance.tcz_user.id == lTrainer.id:
      instance.tcz_user = validated_data['tcz_user']
      instance.save()
      return instance
    else:
      return None

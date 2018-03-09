""" serializer for rest framework """

from rest_framework import serializers
from .models import TczHour
from .views_helper import user_has_reservation


class TczHourSerializer(serializers.ModelSerializer):
    """ serializer for the reserved hour
    """
    class Meta:
        model = TczHour
        fields = ('id',
                  'tcz_date',
                  'tcz_user',
                  'tcz_user_change',
                  'tcz_court',
                  'tcz_hour',
                  'tcz_free',
                  )

    def create(self, validated_data):
        tcz_hour = TczHour(tcz_date=validated_data['tcz_date'],
                           tcz_user=validated_data['tcz_user'],
                           tcz_user_change=validated_data['tcz_user_change'],
                           tcz_court=validated_data['tcz_court'],
                           tcz_hour=validated_data['tcz_hour'],
                           tcz_free=validated_data['tcz_free'])
        if user_has_reservation(validated_data['tcz_user']):
            # user already run out of free reservation hours
            return None
        tcz_hour.save()
        return tcz_hour

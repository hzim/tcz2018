""" views for courtdata """

from datetime import date, timedelta

from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication,\
    BasicAuthentication,\
    TokenAuthentication

from courtstatus.models import TczCourtStatus
from courtreservation.models import TczHour
from courtstatus.serializers import TczCourtStatusSerializer
from courtreservation.serializers import TczHourSerializer


class TczCourtStatusAndHourViewSet(viewsets.ViewSet):
  """
  API endpoint that allows users to be viewed or edited.
  """
  authentication_classes = (SessionAuthentication,
                            BasicAuthentication,
                            TokenAuthentication)

  @list_route()
  def atdate(self, request, format=None):
    """ returns the reserved status from the day specified in the request parameters
    """
    ldate = date(year=int(request.query_params['year']),
                 month=int(request.query_params['month']),
                 day=int(request.query_params['day']))
    tczStatus = TczCourtStatus.objects.filter(lock_date=ldate).order_by('lock_date')
    tczHours = TczHour.objects.filter(tcz_date=ldate).order_by('tcz_date')
    hours = TczHourSerializer(tczHours, many=True)
    status = TczCourtStatusSerializer(tczStatus, many=True)
    combined = status.data + hours.data
    return Response({'status': status.data,
                     'hours': hours.data})

""" command to save all hours to csv file """
from datetime import date
from django.core.management.base import BaseCommand

from courtuser.models import CourtUser
from courtreservation.models import TczHour


class Command(BaseCommand):
  """ restore database to csv file """
  help = 'restore TczHour from csv file'

  def handle(self, *args, **options):
    f = open('hour_2018.csv', mode='r', encoding='iso8859-1')
    # skip headline
    line = next(f)
    for line in f:
      split_str = line.split(';')
      strip_str = list(map(str.strip, split_str))
      # date is in format yyyy-mm--dd
      year = int(strip_str[0][6:10])
      month = int(strip_str[0][3:5])
      day = int(strip_str[0][0:2])
      tcz_hour = TczHour(
          tcz_date=date(year, month, day),
          tcz_user=CourtUser.objects.get(username=strip_str[1]),
          tcz_court=int(strip_str[2]),
          tcz_hour=int(strip_str[3]),
          tcz_free=False if (strip_str[4] == 'False') else True,
          tcz_trainer=False if (strip_str[5] == 'False') else True,
          tcz_user_change=CourtUser.objects.get(username=strip_str[6])
      )

      tcz_hour.save()

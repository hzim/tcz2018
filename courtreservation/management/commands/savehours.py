""" command to save all hours to csv file """
from django.core.management.base import BaseCommand

from courtreservation.models import TczHour


class Command(BaseCommand):
  """ save database to csv file """
  help = 'save the TczHour table to a csv file'

  def handle(self, *args, **options):
    f = open('hour_2018.csv', mode='w', encoding='iso8859-1')
    # print headline
    print("Datum ; Mitglied ; Platz ; Stunde ; Freie Stunde ; Trainer ; Reservierer ;", file=f)
    tczhours = TczHour.objects.all()
    for hour in tczhours:
      print("%02d.%02d.%4d" % (hour.tcz_date.day, hour.tcz_date.month, hour.tcz_date.year), ';',
            hour.tcz_user, ';',
            hour.tcz_court, ';',
            hour.tcz_hour, ';',
            hour.tcz_free, ';',
            hour.tcz_trainer, ';',
            hour.tcz_user_change,
            file=f)

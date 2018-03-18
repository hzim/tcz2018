""" command to delete all hours from the database """
from django.core.management.base import BaseCommand

from courtreservation.models import TczHour


class Command(BaseCommand):
  """ delete all hours from the database """
  help = 'delete all entries in TczHour table'

  def handle(self, *args, **options):
    TczHour.objects.all().delete()

""" tennis court reservation database model """
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


def getSentinelUser():
  """ default user when user is deleted """
  return get_user_model().objects.get_or_create(username='deleted')[0]


class TczHour(models.Model):
  """ database model of the court reservation system """
  tcz_date = models.DateField('Datum')
  tcz_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                               verbose_name='reserviert für',
                               related_name='+',
                               on_delete=models.SET(getSentinelUser))
  tcz_user_change = models.CharField('geändert von', max_length=20, default='Frei')
  tcz_court = models.IntegerField('Platz')
  tcz_hour = models.IntegerField('Stunde', default=0)
  tcz_free = models.BooleanField('Frei', help_text='freier Platz', default=False)
  tcz_trainer = models.BooleanField('Trainer', help_text='Stunde mit Trainer', default=False)

  class Meta:
    ordering = ['tcz_date', 'tcz_court', 'tcz_hour']
    verbose_name = 'Tennisplatz reservierte Stunde'
    verbose_name_plural = 'Tennisplatz reservierte Stunden'

  def __str__(self):
    try:
      return "date=%s court=%d hour=%d user=%s free=%s trainer=%s user_change=%s" % \
             (self.tcz_date.ctime(),
              self.tcz_court,
              self.tcz_hour,
              self.tcz_user,
              self.tcz_free,
              self.tcz_trainer,
              self.tcz_user_change)
    except:
      return "date=None court=%d hour=%d user=%s" % \
          (self.tcz_court, self.tcz_hour, self.tcz_user)

""" custom user model """
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager


class CourtUserManager(UserManager):
  """ inherit from django """
  pass


class MyValidator(UnicodeUsernameValidator):
  regex = r'^[\w\.@+\- ]+$'


class CourtUser(AbstractUser):
  """ inherit from django """
  objects = CourtUserManager()
  # TCZ additional fields
  sendEmail = models.BooleanField('email senden',
                                  help_text='Reservierungsänderungen als email senden',
                                  default=False)
  isSpecial = models.BooleanField('Sonder Mitglied',
                                  help_text='Keine Reservierungseinschränkungen prüfen',
                                  default=False)
  isFreeTrainer = models.BooleanField('Trainer',
                                      help_text='Freie Trainerstunden werden mit diesem Mitglied eingetragen',
                                      default=False)
  isGuest = models.BooleanField('Gastspieler',
                                help_text='Gastspieler',
                                default=True)
  # to allow blanks in username it is necessary to override the username definition from AbstractUser
  # and attach the modified validator to the username
  username_validator = MyValidator()
  username = models.CharField(
      _('username'),
      max_length=150,
      unique=True,
      help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
      validators=[username_validator],
      error_messages={'unique': _("A user with that username already exists."), },
  )

  class Meta:
    # names for the admin page
    verbose_name = 'TCZ Mitglied'
    verbose_name_plural = 'TCZ Mitglieder'

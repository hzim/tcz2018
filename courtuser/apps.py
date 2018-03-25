""" user config """
from django.apps import AppConfig


class UsersConfig(AppConfig):
  """ inherit from django """
  name = 'courtuser'
  verbose_name = 'TCZ Mitglieder'

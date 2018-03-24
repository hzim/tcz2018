""" custom user model """
from django.contrib.auth.models import AbstractUser, UserManager


class CourtUserManager(UserManager):
  """ inherit from django """
  pass


class CourtUser(AbstractUser):
  """ inherit from django """
  objects = CourtUserManager()
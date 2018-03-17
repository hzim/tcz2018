""" custom user model """
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
  """ inherit from django """
  pass


class CustomUser(AbstractUser):
  """ inherit from django """
  objects = CustomUserManager()

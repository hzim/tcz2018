""" custom user model """
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):
    objects = CustomUserManager()

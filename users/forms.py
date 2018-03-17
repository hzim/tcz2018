""" administration forms for users """
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
  """ inherit from django """

  class Meta(UserCreationForm.Meta):
    """ meta class """
    model = CustomUser
    fields = UserCreationForm.Meta.fields


class CustomUserChangeForm(UserChangeForm):
  """ ingerit from django """

  class Meta:
    """ meta class """
    model = CustomUser
    fields = UserChangeForm.Meta.fields

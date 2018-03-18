""" administration forms for courtuser """
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CourtUser


class CourtUserCreationForm(UserCreationForm):
  """ inherit from django """

  class Meta(UserCreationForm.Meta):
    """ meta class """
    model = CourtUser
    fields = UserCreationForm.Meta.fields


class CourtUserChangeForm(UserChangeForm):
  """ ingerit from django """

  class Meta:
    """ meta class """
    model = CourtUser
    fields = UserChangeForm.Meta.fields

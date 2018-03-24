""" administration forms for users """
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CourtUserCreationForm, CourtUserChangeForm
from .models import CourtUser


class CourtUserAdmin(UserAdmin):
  model = CourtUser
  add_form = CourtUserCreationForm
  form = CourtUserChangeForm


admin.site.register(CourtUser, CourtUserAdmin)

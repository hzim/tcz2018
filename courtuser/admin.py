""" administration forms for users """
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CourtUserCreationForm, CourtUserChangeForm
from .models import CourtUser

# change djangos admin list display
UserAdmin.list_display = ('username', 'email', 'is_active', 'date_joined',
                          'sendEmail', 'isSpecial', 'isFreeTrainer')
# add TCZ features to detail display
UserAdmin.fieldsets += ((('TCZ'), {'fields': ('sendEmail', 'isSpecial', 'isFreeTrainer')}),)


class CourtUserAdmin(UserAdmin):
  model = CourtUser
  add_form = CourtUserCreationForm
  form = CourtUserChangeForm


admin.site.register(CourtUser, CourtUserAdmin)

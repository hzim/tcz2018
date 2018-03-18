""" what should be shown in the DJANGO admin page """
from django.contrib import admin

from .models import TczCourtStatus


class TczCourtStatusAdmin(admin.ModelAdmin):
  """ one lock """
  fields = ('lock_date', 'lock_comment')
  list_display = ('lock_date', 'lock_comment')


admin.site.register(TczCourtStatus, TczCourtStatusAdmin)

""" what should be shown in the DJANGO admin page """
from django.contrib import admin

from .models import TczHour


class TczHourAdmin(admin.ModelAdmin):
  """ one hour """
  fields = ('tcz_date', 'tcz_user', 'tcz_court',
            'tcz_hour', 'tcz_user_change', 'tcz_free', 'tcz_trainer')
  list_display = ('tcz_date', 'tcz_user', 'tcz_court',
                  'tcz_hour', 'tcz_user_change', 'tcz_free', 'tcz_trainer')
  list_filter = ('tcz_date', 'tcz_user')
  admin_order_field = 'tcz_date'


admin.site.register(TczHour, TczHourAdmin)

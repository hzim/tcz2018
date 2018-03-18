""" tennis court lock database model """
from django.db import models
from django import forms


class TczCourtStatus(models.Model):
  """ database model of the court lock system """
  lock_date = models.DateField('Datum')
  lock_comment = models.CharField('Kommentar', max_length=100, default='Plätze nicht bespielbar')


class TczCourtStatusForm(forms.ModelForm):
  class Meta:
    model = TczCourtStatus
    fields = '__all__'
    widgets = {
        'lock_date': forms.DateInput(attrs={'type': 'date'}),
    }

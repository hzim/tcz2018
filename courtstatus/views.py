""" views for the court locking app """
import locale
import os

from django.views.generic import CreateView, ListView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import TczCourtStatus, TczCourtStatusForm


def getCourtStatus(iDate):
  """ get court status """
  try:
    if os.name == 'nt':
      locale.setlocale(locale.LC_TIME, "deu_deu")
    else:
      locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
    lStatusMessage = iDate.strftime("%A %d. %B %Y") + ' - ' +\
        TczCourtStatus.objects.all().filter(lock_date=iDate)[0].lock_comment
    return lStatusMessage
  except IndexError:
    return ""


class ViewIndex(ListView):
  """ class based view for list of TczCourtStatus objects """
  template_name = 'courtstatus/index.html'

  def get_queryset(self):
    return TczCourtStatus.objects.all()


class ViewCreate(CreateView):
  """ class based view for create form """
  template_name = 'courtstatus/create.html'
  model = TczCourtStatus
  form_class = TczCourtStatusForm

  def form_valid(self, form):
    # check if the user is allowed to create
    if not self.request.user.isSpecial:
      return HttpResponseRedirect(reverse('courtstatusindex'))
    model = form.save(commit=False)
    model.save()
    return HttpResponseRedirect(reverse('courtstatusindex'))
    # You have to either return an HttpResponse(or subclasses), or define get_absolute_url, success_url, etc


class ViewDelete(DeleteView):
  """ class based view for delete form """
  template_name = 'courtstatus/delete.html'
  model = TczCourtStatus
  # Notice get_success_url is defined here and not in the model, because the model will be deleted

  def get_success_url(self):
    return reverse('courtstatusindex')

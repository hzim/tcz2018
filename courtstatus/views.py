""" views for the court locking app """
from django.views.generic import CreateView, ListView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from .models import TczCourtStatus, TczCourtStatusForm

def getCourtStatus(iDate):
  """ get court status """
  try:
    lStatusMessage = TczCourtStatus.objects.all()[0].lock_comment
    return lStatusMessage
  except IndexError:
    return ""

class ViewIndex(ListView):
  template_name = 'courtstatus/index.html'

  def get_queryset(self):
    return TczCourtStatus.objects.all()


class ViewCreate(CreateView):
  template_name = 'courtstatus/create.html'
  model = TczCourtStatus
  form_class = TczCourtStatusForm

  def form_valid(self, form):
    # Don't call super(..) if you want to process the model further(add timestamp, and other fields, etc)
    # super(ViewCreatePost, self).form_valid(form)
    if not self.request.user.is_superuser:
      return HttpResponseRedirect(reverse('courtstatusindex'))
    model = form.save(commit=False)
    model.save()
    return HttpResponseRedirect(reverse('courtstatusindex'))
    # You have to either return an HttpResponse(or subclasses), or define get_absolute_url, success_url, etc


class ViewDelete(DeleteView):
  template_name = 'courtstatus/delete.html'
  model = TczCourtStatus
  # Notice get_success_url is defined here and not in the model, because the model will be deleted

  def get_success_url(self):
    return reverse('courtstatusindex')

""" views for user """

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication,\
    BasicAuthentication,\
    TokenAuthentication
from courtreservation.constants import TENNIS_PLATZ_USER
from .models import CourtUser
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows users to be viewed or edited.
  """
  queryset = CourtUser.objects.all().order_by('username')
  serializer_class = UserSerializer
  authentication_classes = (SessionAuthentication,
                            BasicAuthentication,
                            TokenAuthentication)


def get_user_list(request, sel_user):
  """ get all users from the database
      sort the list by name and put the selected user on the first place of the selection list
      only logged in superusers will see all other superuser
      logged in normal users will only see normal users
  """
  own_user_name = ""
  selectedUser = []
  if request.user.is_authenticated:
    # print("sel_user=",sel_user.username.strip())
    # print("reqUser=",request.user)
    if sel_user is None:
      sel_user = request.user

    own_user_name = sel_user.username
    # restricted users see all restricted users, special users all special users
    allUsers = CourtUser.objects.all()
    for user in allUsers:
      if request.user.isSpecial:
        if user.isSpecial and not user.is_superuser:
          selectedUser.append(user.username)
      else:
        if not user.isSpecial:
          selectedUser.append(user.username)
  # sort by names and insert current user as first selection entry
  selectedUser.sort()
  selectedUser.insert(0, own_user_name)
  return selectedUser

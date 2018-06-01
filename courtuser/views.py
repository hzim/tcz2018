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
      - logged in superusers will see all other superuser
      - logged in normal users will only see normal users
      - logged in guest users will only see themself
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
    allUsers = CourtUser.objects.none()
    if not request.user.isGuest:
      allUsers = CourtUser.objects.filter(isSpecial=request.user.isSpecial,
                                          is_superuser=False,
                                          isGuest=False).order_by('username')
      for user in allUsers:
        selectedUser.append(user.username)
    # insert current user as first selection entry
    selectedUser.insert(0, own_user_name)
  return selectedUser

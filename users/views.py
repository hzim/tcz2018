""" views for user """

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication,\
    BasicAuthentication,\
    TokenAuthentication
from courts.constants import FREE_USER, TENNIS_PLATZ_USER
from .models import CustomUser
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows users to be viewed or edited.
  """
  queryset = CustomUser.objects.all().order_by('username')
  serializer_class = UserSerializer
  authentication_classes = (SessionAuthentication,
                            BasicAuthentication,
                            TokenAuthentication)


def is_free_user(user_name):
  """ check if user is the free user """
  if user_name == FREE_USER:
    return True
  return False


def is_super_user(user):
  """ check if user is superuser """
  return user.is_superuser


def is_normal_user(user):
  """ check if user is normal user """
  return not user.is_superuser


def get_user_list(request, sel_user):
  """ get all users from the database
      sort the list by name and put the selected user on the first place of the selection list
      only logged in superusers will see all other superuser
      logged in normal users will only see normal users
  """
  own_user_name = ""
  all_users = []
  if request.user.is_authenticated:
    # print("sel_user=",sel_user.username.strip())
    # print("reqUser=",request.user)
    if sel_user is None:
      sel_user = request.user

    own_user_name = sel_user.username
    # super users see all users, normal users only normal users
    users = CustomUser.objects.all()
    superuser = is_super_user(request.user)
    for user in users:
      if superuser:
        if is_super_user(user):
          all_users.append(user.username)
      else:
        if is_normal_user(user) and user.username != TENNIS_PLATZ_USER:
          all_users.append(user.username)
  # sort by names and insert current user as first selection entry
  all_users.sort()
  all_users.insert(0, own_user_name)
  return all_users

""" update the user table from csv file """

from sys import exc_info
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from courtuser.models import CourtUser


class Command(BaseCommand):
  """ update CourtUser table from csv file """
  help = 'presets the CourtUser table'

  def handle(self, *args, **options):
    allUsers = set()

    def make_user_name(lastname, firstname):
      """ make username "Lastname Firstname" first letter uppercase """

      if firstname == '':
        # if no firstname - keep the name like it is
        return lastname

      l_lastname_lower = lastname.lower()
      l_firstname_lower = firstname.lower()
      l_lastname = l_lastname_lower[0:1].upper() + l_lastname_lower[1:]
      l_firstname = l_firstname_lower[0:1].upper() + l_firstname_lower[1:]
      return l_lastname + ' ' + l_firstname

    f = open('user_import_2018.csv', mode='r', encoding='iso8859-1')
    # skip headline
    line = next(f)
    for line in f:
      split_str = line.split(';')
      strip_str = list(map(str.strip, split_str))

      # delete users
      if strip_str[3] == 'D':
        lastname = strip_str[0]
        firstname = strip_str[1]
        email = strip_str[2]
        username = make_user_name(lastname, firstname)
        try:
          user = CourtUser.objects.get(username=username)
          user.delete()
          self.stdout.write(self.style.SUCCESS('user deleted "%s"' % username))
        except ObjectDoesNotExist:
          pass

      # create new users
      if strip_str[3] == 'C':
        lastname = strip_str[0]
        firstname = strip_str[1]
        emailAdr = strip_str[2]
        username = make_user_name(lastname, firstname)
        # check for unique user names
        if username in allUsers:
          self.stdout.write(self.style.SUCCESS('user already existing "%s"' % username))
        else:
          allUsers.add(username)
        # check if user already exists
        isNewUser = not CourtUser.objects.filter(username=username).exists()
        lIsSpecial = True if strip_str[4] == 'X' else False
        lTrainer = True if strip_str[5] == 'X' else False
        lSuperUser = True if strip_str[6] == 'X' else False
        lSendEmail = True if strip_str[7] == 'X' else False
        lIsGuest = True if strip_str[8] == 'X' else False
        lPassword = 'tc4zellerndorf' if lIsSpecial else 'tczellerndorf'
        if isNewUser:
          try:
            if lSuperUser:
              user = CourtUser.objects.create_superuser(username,
                                                        email=emailAdr,
                                                        password=lPassword,
                                                        first_name=firstname,
                                                        last_name=lastname,
                                                        sendEmail=lSendEmail,
                                                        isSpecial=lIsSpecial,
                                                        isGuest=lIsGuest,
                                                        isFreeTrainer=lTrainer)
              self.stdout.write(self.style.SUCCESS('superuser created "%s"' % username))
            else:
              user = CourtUser.objects.create_user(username,
                                                   email=emailAdr,
                                                   password=lPassword,
                                                   first_name=firstname,
                                                   last_name=lastname,
                                                   sendEmail=lSendEmail,
                                                   isSpecial=lIsSpecial,
                                                   isGuest=lIsGuest,
                                                   isFreeTrainer=lTrainer)
              self.stdout.write(self.style.SUCCESS('user created "%s"' % username))
          except ValueError:
            self.stdout.write(self.style.SUCCESS('error "%s"' % exc_info()[0]))
        else:
          user = CourtUser.objects.filter(username=username)[0]
          if user.isGuest:
            self.stdout.write(self.style.SUCCESS('user modified "%s"' % username))
            user.isGuest = False
            user.save()


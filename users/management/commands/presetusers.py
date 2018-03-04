""" update the user table from csv file """

from sys import exc_info
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser


class Command(BaseCommand):
    """ update CustomUser table from csv file """
    help = 'presets the CustomUser table'

    def handle(self, *args, **options):
        allUsers = set()

        def make_user_name(lastname, firstname):
            """ make username "Lastname Firstname" first letter uppercase """
            l_lastname = lastname[0:1].upper() + lastname[1:]
            l_firstname = firstname[0:1].upper() + firstname[1:]
            return (l_lastname + ' ' + l_firstname).strip()

        f = open('user_import_2018.csv', mode='r', encoding='iso8859-1')
        # skip headline
        line = next(f)
        for line in f:
            split_str = line.split(';')
            strip_str = list(map(str.strip, split_str))

            # delete users
            if strip_str[3] == 'D':
                lastname = strip_str[0].lower()
                firstname = strip_str[1].lower()
                email = strip_str[2]
                username = make_user_name(lastname, firstname)
                try:
                    user = CustomUser.objects.get(username=username)
                    user.delete()
                    self.stdout.write(self.style.SUCCESS(
                        'user deleted "%s"' % username))
                except ObjectDoesNotExist:
                    pass

            # enter new users
            if strip_str[3] == 'C':
                lastname = strip_str[0].lower()
                firstname = strip_str[1].lower()
                email = strip_str[2]
                username = make_user_name(lastname, firstname)
                # check for unique user names
                if username in allUsers:
                    self.stdout.write(self.style.SUCCESS(
                        'user already existing "%s"' % username))
                else:
                    allUsers.add(username)
                # check if user already exists
                isNewUser = not CustomUser.objects.filter(
                    username=username).exists()
                try:
                    if isNewUser:
                        user = CustomUser.objects.create_user(username,
                                                              email=email,
                                                              password='tczellerndorf',
                                                              first_name=firstname,
                                                              last_name=lastname)
                        self.stdout.write(self.style.SUCCESS(
                            'user created "%s"' % username))
                except ValueError:
                    self.stdout.write(self.style.SUCCESS(
                        'error "%s"' % exc_info()[0]))

            # enter super users
            if strip_str[3] == 'S':
                lastname = strip_str[0]
                firstname = ""
                email = ""
                username = lastname
                # check if user already exists
                isNewUser = not CustomUser.objects.filter(
                    username=username).exists()
                try:
                    if isNewUser:
                        user = CustomUser.objects.create_superuser(username,
                                                                   email=email,
                                                                   password='tc4zellerndorf',
                                                                   first_name=firstname,
                                                                   last_name=lastname)
                        self.stdout.write(self.style.SUCCESS(
                            'superuser created "%s"' % username))
                except ValueError:
                    self.stdout.write(self.style.SUCCESS(
                        'error "%s"' % exc_info()[0]))

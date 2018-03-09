from datetime import date, datetime, timedelta
import locale
import logging
import os

from django.core.mail import send_mail

from users.models import CustomUser
from users.views import is_free_user, is_super_user, is_normal_user

from .constants import EMAIL_BODY_TEMPLATE, EMAIL_SUBJECT, EMAIL_ADDRESS,\
    EMAIL_ACTIONTEXT, SUCCESS_RESERVATION,\
    MAX_RESERVATION_DAYS,\
    MAX_FUTURE_DAYS,\
    BG_FREE, BG_FREEHOUR, BG_OTHER, BG_OWN,\
    FREE_USER,\
    HOUR_START, HOURS_PER_DAY,\
    MIN_MONTH, MAX_MONTH, FREE_MINUTE,\
    COURT_FAKT, NUM_COURTS,\
    STORE_ERROR, STORE_STORNO, STORE_RESERVATION,\
    ERR_HISTORY_CHANGE,\
    ERR_ONE_HOUR_STORNO,\
    ERR_ONLY_OWN_USER,\
    ERR_HOUR_PER_USER,\
    ERR_DATE_INVALID,\
    ERR_NO_MITGLIED
from .models import TczHour


def date_is_wrong(date_to_show, date_today):
  """ check plausibility of date
  """
  if ((date_to_show.year != date_today.year) or
      (date_to_show.month < MIN_MONTH) or
          (date_to_show.month > MAX_MONTH)
      ):
    return True
  return False


def get_act_hour():
  """ get begin of current and next hour
  """
  time_now = datetime.now()
  act_hour = time_now - timedelta(minutes=time_now.minute,
                                  seconds=time_now.second,
                                  microseconds=time_now.microsecond)
  next_hour = act_hour + timedelta(hours=1)
  # ab Minute 45 nächste volle Stunde ermitteln
  if time_now.minute >= FREE_MINUTE:
    act_hour += timedelta(hours=1)
  return (act_hour, next_hour)


def send_email(tcz_hour, email_action):
  """ if user has no email address -> send email to myself for logging
  """
  if tcz_hour.tcz_user.email is None or tcz_hour.tcz_user.email == "":
    tcz_hour.tcz_user.email = EMAIL_ADDRESS
  # set locale for Date format
  if os.name == 'nt':
    locale.setlocale(locale.LC_TIME, "deu_deu")
  else:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

  subject = EMAIL_SUBJECT
  message = EMAIL_BODY_TEMPLATE % \
      (EMAIL_ACTIONTEXT[email_action],
       tcz_hour.tcz_user_change,
       tcz_hour.tcz_user.username,
       tcz_hour.tcz_court,
       tcz_hour.tcz_date.strftime('%A, %d. %b %Y'),
       tcz_hour.tcz_hour)
  from_email = EMAIL_ADDRESS
  recipient_list = [tcz_hour.tcz_user.email]
  logger = logging.getLogger(__name__)
  if is_super_user(tcz_hour.tcz_user) or tcz_hour.tcz_user.email == EMAIL_ADDRESS:
    # do not send emails for super users
    logger.info("no mail to: " + recipient_list[0] + ": " + message)
  else:
    logger.info("send email to: " + recipient_list[0] + ": " + message)
    send_mail(subject, message, from_email, recipient_list)


class SavedDate():
  """ structure for date
  """

  def __init__(self, i_date):
    self.date = i_date
    self.year = "%4d" % i_date.year
    self.month = "%02d" % i_date.month
    self.day = "%02d" % i_date.day


class ChoiceButton():
  """ information of one checkbox or radiobutton
  """

  def __init__(self, index, name, buttype, disabled, label, bgcolor):
    self.index = index
    self.name = name
    self.type = buttype
    self.disabled = disabled
    self.label = label
    self.bgcolor = bgcolor


def build_next_reservation(tcz_hour, tcz_user):
  """ build the string for the next reservation
  """
  next_reservation = [SUCCESS_RESERVATION %
                      (tcz_hour.tcz_date.day,
                       tcz_hour.tcz_date.month,
                       tcz_hour.tcz_date.year,
                       tcz_hour.tcz_hour,
                       tcz_hour.tcz_court,
                       tcz_user.username
                       )
                      ]
  return next_reservation


def get_next_reservation(i_user):
  """ get the next reservation for the specified user in the future
  """
  try:
    now = datetime.now()
    l_datenow = date.today()
    for tcz_hour in TczHour.objects.filter(tcz_user=i_user)\
                                   .filter(tcz_date__gte=l_datenow)\
                                   .order_by('tcz_date', 'tcz_hour'):
      #print(tcz_hour,' now=',now)
      tcztime = datetime(year=tcz_hour.tcz_date.year,
                         month=tcz_hour.tcz_date.month,
                         day=tcz_hour.tcz_date.day,
                         hour=tcz_hour.tcz_hour
                         )
      if ((tcztime > now) and (not tcz_hour.tcz_free)):
        # print(tcz_hour)
        return tcz_hour
      else:
        pass
    return None
  except:
    return None


def user_has_free_reservation_old(i_user):
  """ not used at the moment - this is the old rule for reservation
      check if the user has one reservation since Monday
      for a normal user only 1 hour per week is allowed
      on Sunday after 21h it is allowed to reserve a new hour if there
      is no reserved hour in the future
  """
  try:
    now = datetime.now()
    l_datenow = date.today()
    weekday = l_datenow.weekday()

    if ((weekday == 6) and (now.hour >= 21)):
      # if weekday = 6 = Sunday and hour > 21h take next Monday
      monday = l_datenow + timedelta(days=1)
    else:
      # else take previous Monday
      monday = l_datenow - timedelta(days=weekday)
    # print('Montag=',monday)

    for tcz_hour in TczHour.objects.filter(tcz_user=i_user)\
        .filter(tcz_date__gte=monday)\
            .order_by('tcz_date', 'tcz_hour'):
      if not tcz_hour.tcz_free:
        # found an already reserved hour for this week
        return tcz_hour

    return None
  except:
    return None


def user_has_reservation(i_user):
  """ for a normal user only 2 hours in the future are allowed
  """
  # there is no limit for superusers
  if is_super_user(i_user):
    return None
  try:
    l_datenow = date.today()
    l_hourcnt = 0
    for tcz_hour in TczHour.objects.filter(tcz_user=i_user)\
        .filter(tcz_date__gte=l_datenow)\
            .order_by('tcz_date', 'tcz_hour'):
      if not tcz_hour.tcz_free:
        # found an already reserved hour for this week
        l_hourcnt += 1
        if l_hourcnt == MAX_RESERVATION_DAYS:
          return l_hourcnt
    return None
  except:
    return None


def make_choice_button(tcz_hour, i_user):
  """make one ChoiceButton dependent on the Model.TczHour and the current user
     - set the checkbox type 'radio' or 'checkbox' and enabled or disabled
     - set the label text = username
     - set the background of the button
  """
  box = ''
  dis = ''
  lusername = ''
  if i_user:
    lusername = i_user.username
  if is_free_user(lusername) or is_super_user(i_user):
    # free and superuser are allowed to change everything
    box = 'checkbox'
  else:
    box = 'radio'
    # buttons are disabled if
    # - user not logged in or
    # - for normal users if the hour is already occupied
    if ((lusername == '') or
        (not is_free_user(tcz_hour.tcz_user.username) and
         (tcz_hour.tcz_user.username != lusername))):
      # normal users are not allowed to change a occupied hour
      dis = 'disabled'

  # set the background color
  bgc = ''
  if is_free_user(tcz_hour.tcz_user.username):
    bgc = BG_FREE
  elif tcz_hour.tcz_user.username != lusername:
    # reserved for somebody else
    if tcz_hour.tcz_free:
      bgc = BG_FREEHOUR
    else:
      bgc = BG_OTHER
  else:
    # reserved for me
    if tcz_hour.tcz_free:
      bgc = BG_FREEHOUR
    else:
      bgc = BG_OWN

  # set the label = username
  lab = tcz_hour.tcz_user.username

  # set the index and the name of the box
  ind = tcz_hour.tcz_court * COURT_FAKT + tcz_hour.tcz_hour
  nam = '%d' % ind
  return ChoiceButton(ind, nam, box, dis, lab, bgc)


def make_choice_table(i_date, i_user):
  """ create an empty ChoiceTable and fill it with the Buttons according
      to the database Model.TczHour
  """
  l_choicetable = {}
  #l_date = TczDate.objects.get(day_date=i_date)
  # preset for date and user when creating a new TczHour
  l_date = i_date
  # read all hours of one day
  # .order_by('tcz_hour','tcz_court')
  l_allhours = TczHour.objects.filter(tcz_date=l_date)
  # fill a set of all existing reservations for this day
  l_hours = {}
  for tcz_hour in l_allhours:
    l_hours[(tcz_hour.tcz_hour, tcz_hour.tcz_court)] = tcz_hour

  # get the free user for unreserved hours
  l_freeuser = CustomUser.objects.get(username=FREE_USER)

  # make all choices for this day
  for l_h in range(HOUR_START, HOUR_START+HOURS_PER_DAY):
    l_choicetable[l_h] = []
    for l_c in range(1, NUM_COURTS+1):
      if (l_h, l_c) in l_hours:
        tcz_hour = l_hours[(l_h, l_c)]
      else:
        tcz_hour = TczHour(tcz_date=l_date,
                           tcz_user=l_freeuser,
                           tcz_court=l_c,
                           tcz_hour=l_h,
                           tcz_free=False)
      choice = make_choice_button(tcz_hour, i_user)
      # choiceTableOld.append(choice)
      l_choicetable[l_h].append(choice)
      # print("%s %s %s" % (tcz_hour.tcz_court,tcz_hour.tcz_hour,tcz_hour.tcz_user.username))

  return l_choicetable


def save_choices(i_date, i_user, i_userlogin, i_choices, i_dangermessages):
  """ check the restrictions on database changes according to the selected user
      returns possible problems or in case of successful database change send an email
  """
  l_result = STORE_ERROR
  if i_user is None:
    i_dangermessages.append(ERR_NO_MITGLIED)
    return STORE_ERROR
  for choice in i_choices:
    l_c = int(choice) // COURT_FAKT
    l_h = int(choice) % COURT_FAKT

    # check the date is ok
    l_today = date.today()
    if date_is_wrong(i_date, l_today):
      i_dangermessages.append(ERR_DATE_INVALID % (
          i_date.day, i_date.month, i_date.year))
      return STORE_ERROR

    # normal users are only allowed to save information till MAX_FUTURE_DAYS
    l_normaluser = is_normal_user(i_user)
    if l_normaluser:
      if i_date > l_today + timedelta(days=MAX_FUTURE_DAYS):
        i_dangermessages.append(ERR_DATE_INVALID % (
            i_date.day, i_date.month, i_date.year))
        return STORE_ERROR

    # create time object for reservation time
    l_tcztime = datetime(
        year=i_date.year, month=i_date.month, day=i_date.day, hour=l_h)

    # get the selected hour from the database
    l_reserved = False
    try:
      tcz_hour = TczHour.objects.filter(
          tcz_date=i_date, tcz_court=l_c, tcz_hour=l_h)[0]
      l_reserved = True
    except:
      # the hour does not exist in the database - create a default TczHour
      l_freeuser = CustomUser.objects.get(username=FREE_USER)
      tcz_hour = TczHour(tcz_date=i_date,
                         tcz_user=l_freeuser,
                         tcz_court=l_c,
                         tcz_hour=l_h,
                         tcz_free=False)

    # there are no more checks for superusers
    # for normal users there are some restriction:
    # - to change in the past
    # - to have more than one reservation in the future if it is not the current hour
    # - to reserve if somebody was faster and the desired hour is already reserved
    l_freehour = False
    if l_normaluser:
      l_acthour, l_nexthour = get_act_hour()

      # dont allow modifications of the past
      if l_tcztime < l_acthour:
        i_dangermessages.append(ERR_HISTORY_CHANGE)
        return STORE_ERROR

      if l_reserved:
        # the hour is already reserved - check if storno is allowed
        if tcz_hour.tcz_user == i_user:
          # Storno of a reserved hour only allowed until 1h before reservation
          if ((not tcz_hour.tcz_free) and ((l_tcztime == l_nexthour) or (l_tcztime == l_acthour))):
            i_dangermessages.append(ERR_ONE_HOUR_STORNO)
            return STORE_ERROR
        else:
          # somebody was faster and the hour is already reserved
          i_dangermessages.append(ERR_ONLY_OWN_USER)
          return STORE_ERROR
      else:
        # this is a new hour to reserve
        if l_tcztime == l_acthour:
          # mark spezial reservations for current hour and next hour after minute 45
          # there is no limit for free hours
          l_freehour = True
        else:
          # for the reservation of an new hour check if the user
          # has not reserved already or within this week
          if user_has_reservation(i_user):
            i_dangermessages.append(ERR_HOUR_PER_USER)
            return STORE_ERROR

    # all checks were successful - store in database
    # if (tcz_hour.tcz_user == i_user):
    if l_reserved:
      # delete the reservation
      tcz_hour.tcz_user_change = i_userlogin.username
      l_result = STORE_STORNO
      send_email(tcz_hour, STORE_STORNO)
      tcz_hour.delete()
    else:
      # save hour for user
      tcz_hour.tcz_user = i_user
      tcz_hour.tcz_free = l_freehour
      tcz_hour.tcz_user_change = i_userlogin.username
      tcz_hour.save()
      # send email
      l_result = STORE_RESERVATION
      send_email(tcz_hour, STORE_RESERVATION)
  return l_result

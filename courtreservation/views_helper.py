""" helper fucntions for view """
from datetime import date, datetime, timedelta
import locale
import logging
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from courtuser.models import CourtUser

from .constants import EMAIL_BODY_TEMPLATE, EMAIL_SUBJECT, EMAIL_ADDRESS,\
    EMAIL_ACTIONTEXT, SUCCESS_RESERVATION,\
    MAX_RESERVATION_DAYS,\
    MAX_FUTURE_DAYS,\
    BG_FREE, BG_FREEHOUR, BG_OTHER, BG_OWN, BG_TPI, BG_TPI_FREE, BG_SUPER_USER,\
    FREE_USER, TPI_NAME,\
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
  if date_to_show.year != date_today.year:
    return True
  if date_to_show.month < MIN_MONTH:
    return True
  if date_to_show.month > MAX_MONTH:
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
  """ send email if user has an email and refistered for email otherwise log event """
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

  logger = logging.getLogger(__name__)
  if tcz_hour.tcz_user.sendEmail and tcz_hour.tcz_user.email and tcz_hour.tcz_user.email != "":
    # send email to users which
    from_email = EMAIL_ADDRESS
    recipient_list = [tcz_hour.tcz_user.email]
    logger.info("send email to: " + recipient_list[0] + ": " + message)
    send_mail(subject, message, from_email, recipient_list)
  else:
    logger.info("no mail to: " + tcz_hour.tcz_user.username + ": " + message)


class SavedDate():
  """ structure for date"""

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
                       tcz_user.username)]
  return next_reservation


def get_next_reservation(iUser):
  """ get the next reservation for the specified user in the future
  """
  try:
    now = datetime.now()
    l_datenow = date.today()
    for tcz_hour in TczHour.objects.filter(tcz_user=iUser)\
                                   .filter(tcz_date__gte=l_datenow)\
                                   .order_by('tcz_date', 'tcz_hour'):
      #print(tcz_hour,' now=',now)
      tcztime = datetime(year=tcz_hour.tcz_date.year,
                         month=tcz_hour.tcz_date.month,
                         day=tcz_hour.tcz_date.day,
                         hour=tcz_hour.tcz_hour)
      if ((tcztime > now) and (not tcz_hour.tcz_free)):
        # print(tcz_hour)
        return tcz_hour
      else:
        pass
    return None
  except ObjectDoesNotExist:
    return None


"""
not used at the moment - this is the old rule for reservation
check if the user has one reservation since Monday
for a normal user only 1 hour per week is allowed
on Sunday after 21h it is allowed to reserve a new hour if there
is no reserved hour in the future

def user_has_free_reservation_old(iUser):
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

    for tcz_hour in TczHour.objects.filter(tcz_user=iUser)\
        .filter(tcz_date__gte=monday)\
            .order_by('tcz_date', 'tcz_hour'):
      if not tcz_hour.tcz_free:
        # found an already reserved hour for this week
        return tcz_hour

    return None
  except:
    return None
"""


def user_has_reservation(iUser):
  """ for a normal user only 2 hours in the future are allowed
  """
  # there is no limit for superusers
  if iUser.isSpecial:
    return None
  try:
    l_datenow = date.today()
    l_hourcnt = 0
    for tcz_hour in TczHour.objects.filter(tcz_user=iUser)\
            .filter(tcz_date__gte=l_datenow).order_by('tcz_date', 'tcz_hour'):
      if not tcz_hour.tcz_free and not tcz_hour.tcz_trainer:
        # found an already reserved hour for this week
        l_hourcnt += 1
        if l_hourcnt == MAX_RESERVATION_DAYS:
          return l_hourcnt
    return None
  except ObjectDoesNotExist:
    return None


def make_choice_button(iCourt, iHour, tcz_hour, iUser):
  """make one ChoiceButton dependent on the Model.TczHour and the current user
     - set the checkbox type 'radio' or 'checkbox' and enabled or disabled
     - set the label text = username
     - set the background of the button
  """
  box = ''
  dis = ''
  lusername = iUser.username
  if iUser.isSpecial:
    # superuser are allowed to change everything
    box = 'checkbox'
  else:
    box = 'radio'
    # check if button should be disabled
    if iUser.is_anonymous:
      # not logged in
      dis = 'disabled'
    if tcz_hour:  # hour is reserved
      if tcz_hour.tcz_user.username != lusername:  # hour is reserved not for me
        if not tcz_hour.tcz_user.isFreeTrainer:  # hour is not reserved for the trainer
          dis = 'disabled'

  # set the background color
  bgc = ''
  if tcz_hour is None:
    bgc = BG_FREE
  elif tcz_hour.tcz_free:
    bgc = BG_FREEHOUR
  elif tcz_hour.tcz_trainer:
    # Trainer is free to reserve
    if tcz_hour.tcz_user.isFreeTrainer:
      # Trainer is free to reserve
      bgc = BG_TPI_FREE
    else:
      # Trainer is reserved
      bgc = BG_TPI
  elif tcz_hour.tcz_user.isSpecial:
    bgc = BG_SUPER_USER
  elif tcz_hour.tcz_user.username == lusername:
    # reserved for me
    bgc = BG_OWN
  else:
    # reserved for somebody else
    bgc = BG_OTHER

  # set the label = username
  lab = FREE_USER
  if tcz_hour:
    if tcz_hour.tcz_trainer and not tcz_hour.tcz_user.isFreeTrainer:
      lab = TPI_NAME + '+' + tcz_hour.tcz_user.username
    else:
      lab = tcz_hour.tcz_user.username

  # set the index and the name of the box
  ind = iCourt * COURT_FAKT + iHour
  nam = '%d' % ind
  return ChoiceButton(ind, nam, box, dis, lab, bgc)


def make_choice_table(i_date, iUser):
  """ create an empty ChoiceTable and fill it with the Buttons according
      to the database Model.TczHour
  """
  l_choicetable = {}
  # preset for date and user when creating a new TczHour
  l_date = i_date
  # read all hours of one day
  l_allhours = TczHour.objects.filter(tcz_date=l_date)
  # fill a set of all existing reservations for this day
  l_hours = {}
  for tcz_hour in l_allhours:
    l_hours[(tcz_hour.tcz_hour, tcz_hour.tcz_court)] = tcz_hour

  # make all choices for this day
  for l_h in range(HOUR_START, HOUR_START+HOURS_PER_DAY):
    l_choicetable[l_h] = []
    for l_c in range(1, NUM_COURTS+1):
      tcz_hour = l_hours[(l_h, l_c)] if (l_h, l_c) in l_hours else None
      choice = make_choice_button(l_c, l_h, tcz_hour, iUser)
      l_choicetable[l_h].append(choice)
      # print("%s %s %s" % (tcz_hour.tcz_court,tcz_hour.tcz_hour,tcz_hour.tcz_user.username))

  return l_choicetable


def save_choices(i_date, iUser, iUserlogin, i_choices, i_dangermessages):
  """ check the restrictions on database changes according to the selected user
      returns possible problems or in case of successful database change send an email
  """
  l_result = STORE_ERROR
  if iUser is None:
    i_dangermessages.append(ERR_NO_MITGLIED)
    return STORE_ERROR
  lTrainer = CourtUser.objects.get(isFreeTrainer=True)
  for choice in i_choices:
    l_c = int(choice) // COURT_FAKT
    l_h = int(choice) % COURT_FAKT

    # check the date is ok
    l_today = date.today()
    if date_is_wrong(i_date, l_today):
      i_dangermessages.append(ERR_DATE_INVALID % (i_date.day, i_date.month, i_date.year))
      return STORE_ERROR

    # normal users are only allowed to save information till MAX_FUTURE_DAYS
    if not iUser.isSpecial:
      if i_date > l_today + timedelta(days=MAX_FUTURE_DAYS):
        i_dangermessages.append(ERR_DATE_INVALID % (i_date.day, i_date.month, i_date.year))
        return STORE_ERROR

    # create time object for reservation time
    l_tcztime = datetime(year=i_date.year, month=i_date.month, day=i_date.day, hour=l_h)

    # get the selected hour from the database
    try:
      exist_hour = TczHour.objects.filter(tcz_date=i_date, tcz_court=l_c, tcz_hour=l_h)[0]
    except (IndexError, ObjectDoesNotExist):
      # the hour does not exist in the database it is free
      exist_hour = None

    # there are no more checks for superusers
    # for normal users there are some restriction:
    # - to change in the past
    # - to have more than one reservation in the future if it is not the current hour
    # - to reserve if somebody was faster and the desired hour is already reserved
    l_freehour = False
    if not iUser.isSpecial:
      l_acthour, l_nexthour = get_act_hour()

      # dont allow modifications of the past
      if l_tcztime < l_acthour:
        i_dangermessages.append(ERR_HISTORY_CHANGE)
        return STORE_ERROR

      if exist_hour:
        # the hour is already reserved - check if storno is allowed
        if exist_hour.tcz_user == iUser:
          # Storno of a reserved hour only allowed until 1h before reservation
          if ((not exist_hour.tcz_free) and ((l_tcztime == l_nexthour) or (l_tcztime == l_acthour))):
            i_dangermessages.append(ERR_ONE_HOUR_STORNO)
            return STORE_ERROR
        # if the reserved hour is not a trainer hour
        else:
          if exist_hour.tcz_trainer: 
            if exist_hour.tcz_user != iUser and exist_hour.tcz_user != lTrainer:
              # somebody was faster and the hour is already reserved
              i_dangermessages.append(ERR_ONLY_OWN_USER)
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
          if user_has_reservation(iUser):
            i_dangermessages.append(ERR_HOUR_PER_USER)
            return STORE_ERROR

    # all checks were successful - store in database
    if exist_hour:
      if not iUser.isSpecial:
        if exist_hour.tcz_trainer:
          # change the user who changed the reservation
          exist_hour.tcz_user_change = iUserlogin.username
          if exist_hour.tcz_user.isFreeTrainer:
            # this is a free trainer hour it will be reserved
            exist_hour.tcz_user = iUser
            exist_hour.save()
            l_result = STORE_RESERVATION
            send_email(exist_hour, STORE_RESERVATION)
            return l_result
          # this trainer hour is reserved for me so it will be canceled
          l_result = STORE_STORNO
          send_email(exist_hour, STORE_STORNO)
          exist_hour.tcz_user = lTrainer
          exist_hour.save()
          return l_result

      # delete the reservation
      exist_hour.tcz_user_change = iUserlogin.username
      l_result = STORE_STORNO
      send_email(exist_hour, STORE_STORNO)
      exist_hour.delete()
    else:
      # save hour for user
      new_hour = TczHour(tcz_date=i_date,
                         tcz_user=iUser,
                         tcz_court=l_c,
                         tcz_hour=l_h,
                         tcz_free=l_freehour,
                         tcz_trainer=iUser.isFreeTrainer,
                         tcz_user_change=iUserlogin.username)
      new_hour.save()
      # send email
      l_result = STORE_RESERVATION
      send_email(new_hour, STORE_RESERVATION)
  return l_result

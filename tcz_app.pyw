#!/usr/local/bin/python3

import argparse
from datetime import date, timedelta, datetime
from tkinter import ttk
import tkinter
import tkinter.messagebox
import math
import locale
import os
from threading import Timer
import sqlite3
from sqlite3 import Error
import urllib.request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
import json
# import django

# imports for working in Django environment
#os.environ['DJANGO_SETTINGS_MODULE'] = 'tcz2018.settings'
# django.setup()

from courtreservation.constants import BG_FREE,\
    BG_OTHER,\
    BG_FREEHOUR,\
    BG_SUPER_USER,\
    BG_TPI_FREE,\
    BG_TPI,\
    TPI_NAME,\
    FREE_MINUTE,\
    HOURS_PER_DAY,\
    MAX_FUTURE_DAYS,\
    MAX_RESERVATION_DAYS,\
    NUM_COURTS,\
    HOUR_START,\
    FREE_USER,\
    ERR_OTHER_USER,\
    ERR_DATE_INVALID,\
    ERR_HOUR_PER_USER,\
    ERR_NO_RESERVATION,\
    ERR_HISTORY_CHANGE

# to allow access to the courts imports and DJANGO environment for database
# sys.path.append('./')

# token for TCZ
HTTP_HEADER = {
    'Authorization': 'Token cc139ab380200e62782e2a6c635683d7d551f1d7',
    'Accept': '*/*',
}

FONT14BOLD = ('Verdana', 14, 'bold')
FONT14NORMAL = ('Verdana', 14)
FONT12BOLD = ('Verdana', 12, 'bold')
FONT10BOLD = ('Verdana', 10, 'bold')
FONT18BOLD = ('Verdana', 18, 'bold')
FONT18NORMAL = ('Verdana', 18)
LAB_BACKGROUND = '#7F7F7F'
INITIAL_USER = 'Bitte auswählen'


def get_act_hour():
  """ get begin of current hour
  """
  time_now = datetime.now()
  act_hour = time_now - timedelta(minutes=time_now.minute,
                                  seconds=time_now.second,
                                  microseconds=time_now.microsecond)
  # ab Minute 45 nächste volle Stunde ermitteln
  if time_now.minute >= FREE_MINUTE:
    act_hour += timedelta(hours=1)
  return act_hour


# indices for COURTUSER table record
USER_ID = 0
USER_USERNAME = 1
USER_SENDEMAIL = 2
USER_IS_SUPERUSER = 3
USER_ISSPECIAL = 4
USER_ISFREETRAINER = 5

# indices for COURTHOUR table record
HOUR_ID = 0
HOUR_DATE = 1
HOUR_USERID = 2
HOUR_USER_CHANGE = 3
HOUR_COURT = 4
HOUR_HOUR = 5
HOUR_FREE = 6
HOUR_TRAINER = 7


def sqlDatabaseInit():
  """ connect to database and create tables
  """
  dbFile = 'tcz_app.sqlite3'
  createCourtUser = """ CREATE TABLE IF NOT EXISTS COURTUSER (
                          id INTEGER PRIMARY KEY,
                          username TEXT,
                          sendEmail INTEGER,
                          is_superuser INTEGER,
                          isSpecial INTEGER,
                          isFreeTrainer INTEGER
                        )
                    """

  createCourtHour = """ CREATE TABLE IF NOT EXISTS COURTHOUR (
                          id INTEGER PRIMARY KEY,
                          tcz_date TEXT,
                          tcz_user INTEGER,
                          tcz_user_change TEXT,
                          tcz_court INTEGER,
                          tcz_hour INTEGER,
                          tcz_free INTEGER,
                          tcz_trainer INTEGER
                        )
                    """
  try:
    dbConn = sqlite3.connect(dbFile, check_same_thread=False)
    # print("SQLLite3 version ", sqlite3.version)
    cursor = dbConn.cursor()
    cursor.execute(createCourtUser)
    cursor.execute(createCourtHour)
    return dbConn
  except Error as e:
    print(e)
    return None


def get_date_text(i_date):
  """ set locale for Date format - windows is different
  """
  if os.name == 'nt':
    locale.setlocale(locale.LC_TIME, "deu_deu")
  else:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
  return i_date.strftime('%A, %d %B %Y')


def get_date_name(i_date):
  """ get date as string year-zero padded month-zero padded day
  """
  return i_date.strftime('%Y-%m-%d')


def name_to_text(iTczUser, iTczHour):
  """ return text
  """
  if iTczHour[HOUR_TRAINER] and not iTczUser[USER_ISFREETRAINER]:
    return TPI_NAME + '+' + iTczUser[USER_USERNAME]
  return iTczUser[USER_USERNAME]


def user_has_reservation(iUser):
  """ for a normal user only 2 hours in the future are allowed
  """
  datenow = get_date_name(date.today())
  stmt = "SELECT * from COURTHOUR where tcz_date>='%s' AND tcz_user=%d" % (datenow, iUser[USER_ID])
  # print(stmt)
  MY_APP.app.dbCursor.execute(stmt)
  lMyHours = MY_APP.app.dbCursor.fetchall()

  # dont count free hours
  lHourCount = 0
  for lHour in lMyHours:
    if not lHour[HOUR_FREE]:
      lHourCount += 1
      if lHourCount == MAX_RESERVATION_DAYS:
        return lHourCount
  return None


def now_string():
  """ returns current date as string
  """
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class ReservationButton():
  """ Button used for the reservation display
  """

  def __init__(self, app, court, hour):
    self.app = app
    self.frame = app.frame2
    self.court = court
    self.hour = hour
    self.but = ttk.Label(self.frame, width=20, text='',
                         font=FONT14BOLD, background=BG_FREE, anchor=tkinter.CENTER)
    self.but.bind("<Button-1>", self.but_pressed)
    self.but.grid(row=self.hour+2-HOUR_START, column=self.court+1,
                  padx=1, pady=1, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

  def but_pressed(self, event):
    """ event when button is pressed
    """
    # print('pressed court=%d, hour=%d' % (self.court,self.hour))
    if self.app.courtUser is None:
      tkinter.messagebox.showerror('Fehler', 'Bitte zuerst Mitglied auswählen')
    else:
      self.app.update_tcz_hour(self.court, self.hour)


class ReservationApp(tkinter.Frame):
  """ the app
  """

  def __init__(self, *args, **kwargs):
    tkinter.Frame.__init__(self, *args, **kwargs)

    self.dbConn = sqlDatabaseInit()
    self.dbCursor = self.dbConn.cursor()

    self.error_http = False
    self.error_url = False
    self.tk_datename = tkinter.StringVar()
    self.user_name = INITIAL_USER
    self.courtUser = None
    self.tk_message = tkinter.StringVar()

    self.frame1 = ttk.Frame(self)
    self.frame2 = ttk.Frame(self)
    self.frame3 = ttk.Frame(self)
    self.frame1.pack(fill=tkinter.X)
    self.frame2.pack(expand=1, fill=tkinter.BOTH)
    self.frame3.pack(fill=tkinter.X)

    self.ui_make_header()
    self.ui_make_main()
    self.ui_make_footer()
    self.get_all_users()
    self.current_date = date.today()
    self.current_date_name = get_date_name(self.current_date)
    self.do_date_today(update=False)
    if GET_HOUR_FROM_SERVER:
      self.get_all_hours()
    else:
      self.get_fromnow_hours()
    # start update timer_all
    self.timer = Timer(30.0, self.update_fromnow_hours)
    self.timer.start()

  def getUserFromId(self, iUserId):
    self.dbCursor.execute('SELECT * from COURTUSER where id=%d' % iUserId)
    return self.dbCursor.fetchone()

  def getUserFromName(self, iUserName):
    self.dbCursor.execute("SELECT * from COURTUSER where username='%s'" % iUserName)
    return self.dbCursor.fetchone()

  def getUserIdTrainer(self):
    self.dbCursor.execute("SELECT id from COURTUSER where isFreeTrainer=1")
    return self.dbCursor.fetchone()[0]

  def request_from_server(self, request, errortext):
    """ request data from server
    """
    self.error_http = False
    self.error_url = False
    try:
      self.response = urllib.request.urlopen(request)
    except HTTPError as e_exc:
      print("server couldn't fulfill the request, Error code: ", e_exc.code, e_exc.reason)
      self.error_http = True
      self.response = None
    except URLError as e_exc:
      print('Failed to reach a server, Reason: ', e_exc.reason)
      self.error_url = True
      self.response = None

    if self.error_url:
      # the server cannot be reached
      self.tk_message.set('%s: Serverproblem %s' % (now_string(), errortext))
      self.lab_message.configure(background='red')
      return False
    if self.error_http:
      # server check of request was not successful
      self.tk_message.set('%s: Serverproblem %s' % (now_string(), errortext))
      self.lab_message.configure(background='orange')
      return False
    # no problems
    self.lab_message.configure(background='green')
    return True

  def get_all_users(self):
    """ get the users from the server database
    """
    # self.allUsers = []
    self.user_names_norm = []
    self.user_names_special = []

    if GET_USER_FROM_SERVER:
      req = urllib.request.Request(URL_GETUSERS, data=None, headers=HTTP_HEADER)
      if self.request_from_server(req, 'Mitgliederliste wird lokal gelesen'):
        # everything is fine
        result = json.loads(self.response.read())
        # print(result)
        # fields = 'id', 'username', 'is_superuser', 'isSpecial', 'isFreeTrainer'
        self.dbCursor.execute('DELETE FROM COURTUSER')
        for item in result:
          # update local database
          stmt = "INSERT INTO COURTUSER VALUES(%d, '%s', %d, %d, %d, %d)" % \
              (item['id'],
               item['username'],
               item['sendEmail'],
               item['is_superuser'],
               item['isSpecial'],
               item['isFreeTrainer']
               )
          # print(stmt)
          self.dbCursor.execute(stmt)

    # fill the name lists for separate for special and normal users
    self.dbCursor.execute('SELECT * FROM COURTUSER ORDER BY username')
    allRows = self.dbCursor.fetchall()
    for lRow in allRows:
      if lRow[USER_ISSPECIAL]:
        if not lRow[USER_IS_SUPERUSER]:
          self.user_names_special.append(lRow[USER_USERNAME])
      else:
        self.user_names_norm.append(lRow[USER_USERNAME])

  def getTczHours(self, url):
    """ get the reserved hours from the server database
    """
    req = urllib.request.Request(url, data=None, headers=HTTP_HEADER, method='GET')
    if self.request_from_server(req, 'Aktualisierung nicht möglich'):
      # everything is fine
      result = json.loads(self.response.read())
      # result contains all reserved hours
      # fields = ('id','tcz_date','tcz_user','tcz_user_change','tcz_court','tcz_hour','tcz_free','tcz_trainer')
      # store the received items to the database
      for item in result:
        stmt = "INSERT INTO COURTHOUR VALUES(%d, '%s', %d, '%s', %d, %d, %d, %d)" % \
            (item['id'],
             item['tcz_date'],
             item['tcz_user'],
             item['tcz_user_change'],
             item['tcz_court'],
             item['tcz_hour'],
             item['tcz_free'],
             item['tcz_trainer'],
             )
        # print(stmt)
        self.dbCursor.execute(stmt)
      return True
    # server problem
    return False

  def get_all_hours(self):
    """ delete local database and fetch all hours from server
    """
    self.dbCursor.execute('DELETE FROM COURTHOUR')
    if self.getTczHours(URL_GETHOURS):
      self.do_update_mainframe()

  def get_fromnow_hours(self):
    """ same as get_all_hours but only from the current date
    """
    lDate = get_date_name(date.today())
    self.dbCursor.execute("DELETE FROM COURTHOUR WHERE tcz_date>='%s'" % lDate)
    if self.getTczHours(URL_GETHOURS_FROMNOW):
      self.do_update_mainframe()

  def get_date_hours(self, i_date):
    """ update the hours for the specified date from the server
    """
    lDate = get_date_name(i_date)
    self.dbCursor.execute("DELETE FROM COURTHOUR WHERE tcz_date='%s'" % lDate)
    if self.getTczHours(URL_GETHOURS_DATE % (i_date.year, i_date.month, i_date.day)):
      self.do_update_mainframe()

  def update_curr_hours(self):
    """ update current date
    """
    self.get_date_hours(self.current_date)

  def update_fromnow_hours(self):
    """ update all relevant reserved hours
    """
    # destroy all data which will be requested
    self.get_fromnow_hours()
    print('restart timer: ' + str(datetime.now()))
    self.timer.cancel()
    self.timer = Timer(3600.0, self.update_fromnow_hours)
    self.timer.start()

  def fetchHour(self, court, hour):
    """ get reserved hour from local database """
    stmt = "SELECT * from COURTHOUR where tcz_date='%s' AND tcz_court=%d AND tcz_hour=%d" % \
        (self.current_date_name, court, hour)
    self.dbCursor.execute(stmt)
    return self.dbCursor.fetchone()

  def updateDateDenied(self, l_tcztime):
    """ normal users are not allowed to change the past """
    if not self.courtUser[USER_ISSPECIAL]:
      l_acthour = get_act_hour()
      if l_tcztime < l_acthour:
        tkinter.messagebox.showerror('Fehler', ERR_HISTORY_CHANGE)
        return True

      l_today = date.today()
      if self.current_date > l_today + timedelta(days=MAX_FUTURE_DAYS):
        l_errormessage = ERR_DATE_INVALID % (l_tcztime.day, l_tcztime.month, l_tcztime.year)
        tkinter.messagebox.showerror('Fehler', l_errormessage)
        return True
    return False

  def isFreeHour(self, l_tcztime):
    if not self.courtUser[USER_ISSPECIAL]:
      l_acthour = get_act_hour()
      if l_tcztime == l_acthour:
        # mark spezial reservations for current hour and next hour after minute 45
        # there is no limit for free hours
        return True
    return False

  def delete_tcz_hour(self, iHour):
    """ delete the hour
    """
    print('Delete Datum=%s Stunde=%s Platz=%s username=%s' %
          (self.current_date_name, iHour[HOUR_HOUR], iHour[HOUR_COURT], self.courtUser[USER_USERNAME]))
    req = urllib.request.Request(URL_POSTHOUR % iHour[HOUR_ID],
                                 data=None,
                                 headers=HTTP_HEADER,
                                 method='DELETE')
    if self.request_from_server(req, 'Stunde kann nicht storniert werden'):
      # everything is fine - refresh current day from server
      self.tk_message.set('%s: Stornierung für %s durchgeführt' % (now_string(), self.courtUser[USER_USERNAME]))
      self.get_date_hours(self.current_date)

  def insert_tcz_hour(self, court, l_tcztime):
    """ reserve one hour
    """
    l_freehour = self.isFreeHour(l_tcztime)
    l_trainer = self.courtUser[USER_ISFREETRAINER]

    if not l_freehour:
      if user_has_reservation(self.courtUser):
        tkinter.messagebox.showerror('Fehler', ERR_HOUR_PER_USER)
        return

    print('Insert Datum=%s Stunde=%s court=%s user=%s' %
          (self.current_date_name, l_tcztime.hour, court, self.courtUser[USER_USERNAME]))
    l_post = {'tcz_date': self.current_date_name,
              'tcz_user': self.courtUser[USER_ID],
              'tcz_user_change': 'Tennisplatz',
              'tcz_court': court,
              'tcz_hour': l_tcztime.hour,
              'tcz_free': l_freehour,
              'tcz_trainer': l_trainer,
              }
    # encode data to a byte stream
    params = urlencode(l_post).encode('utf-8')

    req = urllib.request.Request(URL_GETHOURS, data=params, headers=HTTP_HEADER, method='POST')
    if self.request_from_server(req, ERR_NO_RESERVATION % self.courtUser[USER_USERNAME]):
      # refresh from the server
      self.tk_message.set('%s: Reservierung für %s durchgeführt' % (now_string(), self.courtUser[USER_USERNAME]))
      self.get_date_hours(self.current_date)

  def update_trainer_hour(self, iTczHour, iNewUserId):
    """ update one hour
    """
    l_freehour = False
    l_trainer = True

    print('Update id=%d, Datum=%s Stunde=%s court=%s user=%s newId=%d' %
          (iTczHour[HOUR_ID], self.current_date_name, iTczHour[HOUR_HOUR], iTczHour[HOUR_COURT], self.courtUser[USER_USERNAME], iNewUserId))
    l_post = {'id': iTczHour[HOUR_ID],
              'tcz_date': iTczHour[HOUR_DATE],
              'tcz_user': iNewUserId,
              'tcz_user_change': 'Tennisplatz',
              'tcz_court': iTczHour[HOUR_COURT],
              'tcz_hour': iTczHour[HOUR_HOUR],
              'tcz_free': l_freehour,
              'tcz_trainer': l_trainer,
              }
    # encode data to a byte stream
    params = urlencode(l_post).encode('utf-8')

    urlstring = URL_PUTHOURS % iTczHour[HOUR_ID]
    print(urlstring)
    req = urllib.request.Request(urlstring, data=params, headers=HTTP_HEADER, method='PATCH')
    if self.request_from_server(req, ERR_NO_RESERVATION % self.courtUser[USER_USERNAME]):
      # refresh from the server
      self.tk_message.set('%s: Reservierung für %s durchgeführt' % (now_string(), self.courtUser[USER_USERNAME]))
      self.get_date_hours(self.current_date)

  def update_tcz_hour(self, court, hour):
    """ update/insert/delete the selected hour
    """
    l_tcztime = datetime(year=self.current_date.year,
                         month=self.current_date.month,
                         day=self.current_date.day,
                         hour=hour)
    if self.updateDateDenied(l_tcztime):
      return
    lTczHour = self.fetchHour(court, hour)
    if lTczHour:
      if self.courtUser[USER_ISSPECIAL]:
        # special users will delete already reserved hours
        self.delete_tcz_hour(lTczHour)
      else:
        # normal users are allowed to change free trainer hours
        # or storno there own reservations
        if lTczHour[HOUR_TRAINER]:
          # this is a trainer hour
          lTrainerId = self.getUserIdTrainer()
          # print('hourid=%d, userid=%d' % (lTczHour[HOUR_USERID], self.courtUser[USER_ID]))
          if lTczHour[HOUR_USERID] == self.courtUser[USER_ID]:
            # storno for trainer - set user to trainer
            lNewUserId = lTrainerId
            self.update_trainer_hour(lTczHour, lNewUserId)
          else:
            # reserve trainer if the hour is free (userid=trainer)
            if lTczHour[HOUR_USERID] == lTrainerId:
              lNewUserId = self.courtUser[USER_ID]
              self.update_trainer_hour(lTczHour, lNewUserId)
            else:
              oldUser = self.getUserFromId(lTczHour[HOUR_USERID])
              tkinter.messagebox.showerror('Fehler', ERR_OTHER_USER % oldUser[USER_USERNAME])
        else:
          if lTczHour[HOUR_USERID] == self.courtUser[USER_ID] or self.courtUser[USER_ISSPECIAL]:
            self.delete_tcz_hour(lTczHour)
          else:
            oldUser = self.getUserFromId(lTczHour[HOUR_USERID])
            tkinter.messagebox.showerror('Fehler', ERR_OTHER_USER % oldUser[USER_USERNAME])
    else:
      # hour not existing - insert a new reservation
      self.insert_tcz_hour(court, l_tcztime)

  def ui_make_header(self):
    """ make the header of the app
    """
    style = ttk.Style()
    style.configure('Date.TButton', font=FONT18BOLD)
    self.but_prev = ttk.Button(self.frame1, text='<', command=self.do_date_prev, style='Date.TButton')
    self.but_next = ttk.Button(self.frame1, text='>', command=self.do_date_next, style='Date.TButton')
    self.but_today = ttk.Button(self.frame1, text='Heute', command=self.do_date_today, style='Date.TButton')
    self.lab_date = ttk.Label(self.frame1, textvariable=self.tk_datename,
                              font=FONT18BOLD,
                              width=25)
    self.lab_hint = ttk.Label(self.frame1, text='Reservieren/Freigeben für:',
                              font=FONT14NORMAL)
    self.lab_hint.bind("<Double-1>", self.ui_make_user_super)
    self.but_user = ttk.Button(self.frame1, text=self.user_name, style='Date.TButton', width=25)
    self.but_user.bind("<Button-1>", self.ui_make_user_normal)
    self.but_today.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.but_prev.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.lab_date.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.but_next.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5)
    self.lab_hint.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5, anchor='w')
    self.but_user.pack(side=tkinter.LEFT, padx=3, pady=3, ipadx=5, ipady=5, expand=1, fill=tkinter.X)

  def ui_make_main(self):
    """ make the main window
    """
    # let the row grow (weight=1)
    tkinter.Grid.rowconfigure(self.frame2, 1, weight=1)
    # tkinter.Grid.columnconfigure(self.frame2, 1, weight=1)
    self.all_buttons = []

    l_lab = ttk.Label(self.frame2, text='Stunde', width=10,
                      font=FONT14BOLD, background=LAB_BACKGROUND, anchor=tkinter.CENTER)
    l_lab.grid(row=1, column=1, padx=3, pady=3, sticky=tkinter.N+tkinter.S)
    for i in range(NUM_COURTS):
      tkinter.Grid.columnconfigure(self.frame2, i+2, weight=1)
      l_lab = ttk.Label(self.frame2, text='Platz %d' % (i+1),
                        font=FONT14BOLD, background=LAB_BACKGROUND, anchor=tkinter.CENTER)
      l_lab.grid(row=1, column=i+2, padx=3, pady=3, sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

    l_row = 1
    for hour in range(HOUR_START, HOUR_START+HOURS_PER_DAY):
      l_row += 1
      tkinter.Grid.rowconfigure(self.frame2, l_row, weight=1)
      l_lab = ttk.Label(self.frame2, text='%d' % hour, width=10,
                        font=FONT14BOLD, background=LAB_BACKGROUND, anchor=tkinter.CENTER)
      l_lab.grid(row=l_row, column=1, padx=3, pady=3, sticky=tkinter.N+tkinter.S)
    for court in range(NUM_COURTS):
      for hour in range(HOUR_START, HOUR_START+HOURS_PER_DAY):
        self.all_buttons.append(ReservationButton(self, court+1, hour))

  def do_update_mainframe(self):
    """ update the main frame
    """
    self.last_udpate_time = datetime.now()
    l_allreserved = set()
    self.dbCursor.execute("SELECT * from COURTHOUR where tcz_date='%s'" % self.current_date_name)
    lAllHours = self.dbCursor.fetchall()
    # print("allhours=", lAllHours, self.current_date_name)
    for l_tczhour in lAllHours:
      cbindex = (l_tczhour[HOUR_COURT] - 1) * HOURS_PER_DAY + l_tczhour[HOUR_HOUR] - HOUR_START
      # print(cbindex,l_tczhour)
      l_courtUser = self.getUserFromId(l_tczhour[HOUR_USERID])
      # print(l_tcz_user)
      l_but_text = name_to_text(l_courtUser, l_tczhour)
      self.all_buttons[cbindex].but.configure(text=l_but_text)
      if l_tczhour[HOUR_FREE]:
        self.all_buttons[cbindex].but.configure(background=BG_FREEHOUR)
      elif l_tczhour[HOUR_TRAINER]:
        if l_courtUser[USER_ISFREETRAINER]:
          self.all_buttons[cbindex].but.configure(background=BG_TPI_FREE)
        else:
          self.all_buttons[cbindex].but.configure(background=BG_TPI)
      elif l_courtUser[USER_ISSPECIAL]:
        self.all_buttons[cbindex].but.configure(background=BG_SUPER_USER)
      else:
        self.all_buttons[cbindex].but.configure(background=BG_OTHER)
      # add the index to the reserved hours
      l_allreserved.add(cbindex)

    # now update all fields which should be free
    cbindex = 0
    for l_cb in self.all_buttons:
      # print('%s index=%d' % (l_cb.text,cbindex))
      if (l_cb.but.cget('text') != FREE_USER and cbindex not in l_allreserved):
        l_cb.but.configure(text=FREE_USER)
        l_cb.but.configure(background=BG_FREE)
      cbindex += 1

  def ui_make_footer(self):
    """ make the footer of the app
    """
    style = ttk.Style()
    style.configure('Refresh.TButton', font=FONT18NORMAL)
    self.tk_message.set('')
    self.lab_message = ttk.Label(self.frame3, textvariable=self.tk_message, font=FONT18NORMAL)
    self.but_refresh = ttk.Button(self.frame3, text='Aktualisieren',
                                  command=self.update_curr_hours,
                                  style='Refresh.TButton')
    self.lab_message.pack(expand=1, fill=tkinter.X, side=tkinter.LEFT)
    self.but_refresh.pack()

  def ui_make_user_window(self, i_super):
    """ make the user window
    """
    self.user_win = tkinter.Toplevel(self)
    self.user_win.wm_title("Wähle Mitglied")
    tframe = ttk.Frame(self.user_win)
    tframe.pack(expand=1, fill=tkinter.BOTH)
    if os.name != 'nt':
      self.user_win.attributes('-zoomed', True)  # maximize window
    # load the user list for normal or superusers
    if i_super:
      l_users = self.user_names_special
    else:
      l_users = self.user_names_norm
    l_namecount = len(l_users)
    l_columns = 7
    l_rows = int(math.ceil(l_namecount / l_columns))
    # configure the rows and columns to resize
    for l_col in range(l_columns):
      tkinter.Grid.columnconfigure(tframe, l_col, weight=1)
    for l_row in range(l_rows):
      tkinter.Grid.rowconfigure(tframe, l_row, weight=1)
    # build the labels for all usernames
    for l_row in range(l_rows):
      for l_col in range(l_columns):
        namind = l_row*l_columns + l_col
        # the last row is probably not filled to the end
        if namind < l_namecount:
          label = ttk.Label(tframe, width=20, text=l_users[namind],
                            font=FONT14BOLD, background='white')
          label.bind("<Button-1>", self.do_select_user)
          label.grid(row=l_row, column=l_col, padx=2, pady=2)

  def ui_make_user_super(self, event):
    """ make window for super users
    """
    self.ui_make_user_window(True)

  def ui_make_user_normal(self, event):
    """ make window for normal users
    """
    self.ui_make_user_window(False)

  def do_select_user(self, event):
    """ update the user with the selected one
    """
    self.user_name = event.widget.cget('text')
    self.courtUser = self.getUserFromName(self.user_name)
    self.but_user.configure(text=self.user_name)
    self.user_win.destroy()

  def do_date_prev(self):
    """ move one day back
    """
    self.current_date = self.current_date + timedelta(days=-1)
    self.tk_datename.set(get_date_text(self.current_date))
    self.current_date_name = get_date_name(self.current_date)
    self.do_update_mainframe()

  def do_date_next(self):
    """ move one day forward
    """
    self.current_date = self.current_date + timedelta(days=1)
    self.tk_datename.set(get_date_text(self.current_date))
    self.current_date_name = get_date_name(self.current_date)
    self.do_update_mainframe()

  def do_date_today(self, update=True):
    """ move to the current date
    """
    self.current_date = date.today()
    self.tk_datename.set(get_date_text(self.current_date))
    self.current_date_name = get_date_name(self.current_date)
    if update:
      self.do_update_mainframe()

# ---------------------------------------------------------------------


class MainWindow:
  """ build the main window
  """

  def __init__(self):
    self.tk_tk = tkinter.Tk()
    self.tk_tk.protocol("WM_DELETE_WINDOW", self.do_destroy_main_window)
    self.tk_tk.wm_title("Tennisplatz Reservierung")
    if os.name != 'nt':
      # attributes only works for UNIX
      self.tk_tk.attributes('-zoomed', True)  # maximize window
    self.app = ReservationApp(self.tk_tk)
    self.app.pack(side="top", fill="both", expand=True)
    self.state = False
    self.tk_tk.bind("<F11>", self.toggle_fullscreen)
    self.tk_tk.bind("<Escape>", self.end_fullscreen)

  def do_destroy_main_window(self):
    """ destroy myself
    """
    if tkinter.messagebox.askokcancel("Beenden", "Programm beenden?"):
      self.app.timer.cancel()
      self.app.dbConn.commit()
      self.app.dbConn.close()
      self.tk_tk.destroy()

  def toggle_fullscreen(self, event=None):
    """ toggle the fullscreen mode
    """
    self.state = not self.state  # Just toggling the boolean
    if os.name != 'nt':
      self.tk_tk.attributes("-fullscreen", self.state)
    return "break"

  def end_fullscreen(self, event=None):
    """ stop the full screen mode
    """
    self.state = False
    if os.name != 'nt':
      self.tk_tk.attributes("-fullscreen", False)
    return "break"


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="app for tcz reservation")
  parser.add_argument("-l", "--localhost",
                      help="connect to localhost (django development server)",
                      action="store_true")
  parser.add_argument("-r", "--reservedhours",
                      help="Reservierte Stunden aus der Vergangenheit vom Server holen",
                      action="store_true")
  parser.add_argument("-u", "--users",
                      help="Mitgliederliste vom Server holen",
                      action="store_true")
  args = parser.parse_args()
  GET_HOUR_FROM_SERVER = args.reservedhours
  GET_USER_FROM_SERVER = args.users
  if args.localhost:
    # imports to use Django REST framework
    URL_GETUSERS = 'http://127.0.0.1:8000/tczusers.json/'
    URL_GETHOURS = 'http://127.0.0.1:8000/tczhours.json/'
    URL_PUTHOURS = 'http://127.0.0.1:8000/tczhours/%d/'
    URL_GETHOURS_DATE = 'http://127.0.0.1:8000/tczhours/atdate.json/?year=%d&month=%d&day=%d'
    URL_GETHOURS_FROMNOW = 'http://127.0.0.1:8000/tczhours/fromnow.json/'
    URL_POSTHOUR = 'http://127.0.0.1:8000/tczhours/%s/'
  else:
    URL_GETUSERS = 'https://tczellerndorf.pythonanywhere.com/tczusers.json/'
    URL_GETHOURS = 'https://tczellerndorf.pythonanywhere.com/tczhours.json/'
    URL_PUTHOURS = 'https://tczellerndorf.pythonanywhere.com/tczhours/%d/'
    URL_GETHOURS_DATE = 'https://tczellerndorf.pythonanywhere.com/tczhours/atdate.json/?year=%d&month=%d&day=%d'
    URL_GETHOURS_FROMNOW = 'https://tczellerndorf.pythonanywhere.com/tczhours/fromnow.json/'
    URL_POSTHOUR = 'https://tczellerndorf.pythonanywhere.com/tczhours/%s/'
  MY_APP = MainWindow()
  MY_APP.tk_tk.mainloop()

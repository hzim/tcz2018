# constants for views
NUM_COURTS = 6
HOURS_PER_DAY = 14
HOUR_START = 8

MAX_FUTURE_DAYS = 14
MIN_MONTH = 1
MIN_DAY = 10
MAX_MONTH = 12

MAX_RESERVATION_DAYS = 2

# constants for management commands
MAX_DAYS = 350
START_YEAR = 2017
START_MONTH = 3
START_DAY = 1

END_MONTH = 12
END_DAY = 1

# free username
FREE_USER = 'Frei'
# username for kivy app
APP_USER = 'TCZ'

# superusers usernames
SUPER_USERS = ('Frei',
               'TCZ',
               'TPI',
               'Damen1',
               'Damen2',
               'Damen35',
               'Damen45',
               'Herren1',
               'Herren2',
               'Herren3',
               'Herren35_1',
               'Herren35_2',
               'Herren55',
               'Herren65',
               'Jugend',
              )
TENNIS_PLATZ_USER = 'Tennisplatz'

# offset for court in checkbox id - the checkbox id is calculated
# COURT_FAKT*courtnumber + hour
COURT_FAKT = 100

# Eintragen einer Stunde die nicht als Reservierung zählt ab Minute 45
FREE_MINUTE = 45

#some colors for backgrounds
BG_FREE = "#e4e4e4"
BG_OWN = "#FF7FFF"
BG_OTHER = "#7FFFFF"
BG_FREEHOUR = "#CFCFCF"

BG_KIVY_FREE = [0.2, 0.2, 0.2, 1]
BG_KIVY_RESERVED = [0.23, 0.23, 0.70, 1.0]

# results from saveChoices
STORE_ERROR = 0
STORE_STORNO = 1
STORE_RESERVATION = 2

ERR_HOUR_PER_USER = "Nur 2 Vorreservierungen pro Mitglied erlaubt"
ERR_ONE_HOUR_STORNO = "Stornierung bis maximal 1h vor Beginn möglich"
ERR_HISTORY_CHANGE = "Änderung in der Vergangenheit nicht erlaubt"
ERR_NO_MITGLIED = "Mitglied nicht in Datenbank"
ERR_DATE_INVALID = "Datum %02d.%02d.%04d nicht zulässig"
ERR_DATE_INVALID_STR = "Datum %s.%s.%s nicht zulässig"
ERR_ONLY_OWN_USER = "Platz ist leider schon schon reserviert"
ERR_NO_RESERVATION = 'Diese Stunde kann leider nicht mehr für %s reserviert werden'
ERR_OTHER_USER = 'Stunde bereits von %s reserviert'

INFO_LOGIN = "für Reservierungen bitte zuerst anmelden"
INFO_USER = "für Reservierungen bitte zuerst Mitglied auswählen"

SUCCESS_NORESERVATION = "keine Reservierung für %s"
SUCCESS_STORNO = "%02d.%02d.%04d %02d Uhr Platz=%d storniert für %s"
SUCCESS_RESERVATION = "%02d.%02d.%04d %02d Uhr Platz=%d reserviert für %s"

EMAIL_ADDRESS = "zellerndorfertc@gmail.com"
EMAIL_SUBJECT = "Tennisplatz Reservierung"
EMAIL_BODY_TEMPLATE = "Tennisplatz %s: von %s für %s, Platz=%d, Zeit=%s, %02d Uhr"
EMAIL_ACTIONTEXT = ["", "Stornierung", "Reservierung"]

APP_USERS_PER_PAGE = 78      # sollte ein vielfaches des Grid Rasters sein

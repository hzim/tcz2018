""" views for the court app """
from datetime import date, timedelta
import logging
import os
import locale

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from users.models import CustomUser
from users.views import get_user_list, is_normal_user

from .constants import \
    INFO_LOGIN,\
    ERR_DATE_INVALID,\
    ERR_DATE_INVALID_STR,\
    SUCCESS_NORESERVATION

from .views_helper import \
    make_choice_table,\
    get_next_reservation,\
    build_next_reservation,\
    date_is_wrong,\
    save_choices,\
    SavedDate
from .serializers import TczHourSerializer
from .models import TczHour


class TczHourViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows hours to be viewed or edited.
    """
    queryset = TczHour.objects.all().order_by('tcz_date')
    serializer_class = TczHourSerializer

    @list_route()
    def fromnow(self, request, format=None):
        """ returns the reserved hours from l_today on
        """
        from_hours = TczHour.objects.filter(
            tcz_date__gte=date.today()).order_by('tcz_date')
        page = self.paginate_queryset(from_hours)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(from_hours, many=True)
        return Response(serializer.data)

    @list_route()
    def atdate(self, request, format=None):
        """ returns the reserved hours from the day specified in the request parameters
        """
        # print(request.query_params)
        # print(request.query_params['year'],request.query_params['month'],request.query_params['day'])
        ldate = date(year=int(request.query_params['year']),
                     month=int(request.query_params['month']),
                     day=int(request.query_params['day']))
        from_hours = TczHour.objects.filter(
            tcz_date=ldate).order_by('tcz_date')
        serializer = self.get_serializer(from_hours, many=True)
        return Response(serializer.data)


def redirect_to_date(request, to_date):
    """ redirects to render the updated form
    """
    return HttpResponseRedirect(reverse('courts',
                                        kwargs={'year': '%04d' % to_date.year,
                                                'month': '%02d' % to_date.month,
                                                'day': '%02d' % to_date.day,
                                                }
                                        )
                                )


def render_form(request, sel_user, date_to_show, danger_messages):
    """ collect the data which is needed and call the DJANGO template render function
    """
    # get all users for user selection
    all_users = get_user_list(request, sel_user)
    #  print("makechoice1 %s" % datetime.now())
    choice_table = make_choice_table(date_to_show, sel_user)
    # print("makechoice2 %s" % datetime.now())
    # print(sel_user)
    saved_date = SavedDate(date_to_show)
    success_messages = []
    info_messages = []

    if request.user.is_authenticated:
        tcz_hour = get_next_reservation(sel_user)
        if tcz_hour is None:
            success_messages = [SUCCESS_NORESERVATION % sel_user.username]
        else:
            success_messages = build_next_reservation(tcz_hour, sel_user)
    else:
        info_messages = [INFO_LOGIN]
    # set locale for Date format
    if os.name == 'nt':
        locale.setlocale(locale.LC_TIME, "deu_deu")
    else:
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
    week_day = date_to_show.strftime('%A')

    return render(request, 'courts/courts.html',
                  {'requestDate': '%04d-%02d-%02d' % (date_to_show.year,
                                                      date_to_show.month,
                                                      date_to_show.day,),
                   'weekday': week_day,
                   'savedDate': saved_date,
                   'choiceTable': choice_table,
                   'dangerMessages': danger_messages,
                   'successMessages': success_messages,
                   'infoMessages': info_messages,
                   'allUsers': all_users,
                   })


# ---------------------Function based views -----------------------

# home page - help page
def home(request):
    """ renders the home page
    """
    return render(request, 'courts/home.html')

# ---------------------Function based views -----------------------
# courts page


def courts(request, year='0', month='0', day='0'):
    """ django view function
    """
    # check the requested date
    try:
        if int(year) == 0:
            # page is called without date -> redirect to today
            return redirect_to_date(request, date.today())
        l_datetoshow = date(int(year), int(month), int(day))
    except ValueError:
        # request with invalid date -> inform user and set date to today
        danger_messages = [ERR_DATE_INVALID_STR % (day, month, year)]
        return render_form(request, None, date.today(), danger_messages)

    l_today = date.today()
    selected_user = ""
    if request.method == "POST":
        logger = logging.getLogger("django.request")
        logger.debug(request.POST)
        #oldDate = date(year,month,day)

        # get the selected user or the logged in user
        sel_user = None
        if request.user.is_authenticated:
            # 1st check if a new user is selected from the user selection list
            # store the new selected user in session data
            try:
                selected_user = request.POST.getlist('selectedUser')[0]
                sel_user = CustomUser.objects.get(username=selected_user)
                request.session['SelUser'] = selected_user
            except (IndexError, ObjectDoesNotExist):
                pass
            # 2nd take the user from the session data
            if selected_user == "":
                try:
                    selected_user = request.session['SelUser']
                    sel_user = CustomUser.objects.get(username=selected_user)
                except (KeyError, ObjectDoesNotExist):
                    pass
            # 3rd selected user is equal to logged in user
            if selected_user == "":
                sel_user = request.user

        if 'SetDate' in request.POST:
            new_date = l_today
            try:
                # validate the requested date and change date
                setdate = request.POST.getlist('requestDate')[0].split("-")
                day = int(setdate[2])
                month = int(setdate[1])
                year = int(setdate[0])
                new_date = date(year, month, day)
                if is_normal_user(request.user):
                    if date_is_wrong(new_date, l_today):
                        raise ValueError('MAX_HISTORY_DAYS')
                # set the new date
                l_datetoshow = new_date
            except (ValueError, IndexError):
                danger_messages = [ERR_DATE_INVALID %
                                   (new_date.day, new_date.month, new_date.year)]
                return render_form(request, sel_user, l_datetoshow, danger_messages)
        elif 'SetUser' in request.POST:
            pass
        elif 'DayForward' in request.POST:
            # set date +1 day
            new_date = l_datetoshow + timedelta(days=1)
            if date_is_wrong(new_date, l_today):
                danger_messages = [ERR_DATE_INVALID %
                                   (new_date.day, new_date.month, new_date.year)]
                return render_form(request, sel_user, l_datetoshow, danger_messages)
            else:
                # set the new date
                l_datetoshow = new_date
        elif 'DayBack' in request.POST:
            # set date -1 day
            new_date = l_datetoshow - timedelta(days=1)
            if date_is_wrong(new_date, l_today):
                danger_messages = [ERR_DATE_INVALID %
                                   (new_date.day, new_date.month, new_date.year)]
                return render_form(request, sel_user, l_datetoshow, danger_messages)
            else:
                # set the new date
                l_datetoshow = new_date
        elif 'SetHour' in request.POST:
            # save the requested court(s)
            try:
                choices = request.POST.getlist('choice')
            except:
                choices = []
            danger_messages = []
            if save_choices(l_datetoshow, sel_user, request.user, choices, danger_messages) == 0:
                return render_form(request, sel_user, l_datetoshow, danger_messages)
        # logger = logging.getLogger("")
        # logger.debug("POST l_datetoshow=%d.%d.%d" %
        # (l_datetoshow.day,l_datetoshow.month,l_datetoshow.year))
        return redirect_to_date(request, l_datetoshow)
    else:
        # GET request: display the form
        danger_messages = []
        sel_user = None
        try:
            sel_user = CustomUser.objects.get(
                username=request.session['SelUser'])
        except (KeyError, ObjectDoesNotExist):
            sel_user = None
        if sel_user is None:
            if request.user:
                sel_user = request.user
        return render_form(request, sel_user, l_datetoshow, danger_messages)

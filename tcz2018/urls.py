"""tcz2018 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from rest_framework import routers

from courtreservation.views import helppage, courtreservation, TczHourViewSet
from courtuser.views import UserViewSet
from courtstatus.views import ViewIndex, ViewCreate, ViewDelete


# rest framwork
router = routers.DefaultRouter()
router.register(r'tczusers', UserViewSet)
router.register(r'tczhours', TczHourViewSet)

urlpatterns = [
    url(r'^$', helppage, name='helppage'),
    url(r'^anmelden/', include('allauth.urls')),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/',
        courtreservation, name='courtreservation'),
    #url(r'^user_login/$', auth_views.login, {'template_name': 'courtuser/login.html'}, name='user_login'),
    #url(r'^user_logout/$', auth_views.logout, {'next_page': '/'}, name='user_logout'),
    #url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'courtuser/password_reset.html'}, name='password_reset'),
    #url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    #url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #    auth_views.password_reset_confirm, name='password_reset_confirm'),
    #url(r'^password_reset_complete$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^courtstatus/?$', ViewIndex.as_view(), name='courtstatusindex'),
    url(r'^courtstatus/create/$', ViewCreate.as_view(), name='courtstatuscreate'),
    url(r'^courtstatus/delete/(?P<pk>\d+)/$', ViewDelete.as_view(), name='courtstatusdelete'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

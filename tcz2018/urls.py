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

from courts.views import home, courts, TczHourViewSet
from users.views import UserViewSet


# rest framwork
router = routers.DefaultRouter()
router.register(r'tczusers', UserViewSet)
router.register(r'tczhours', TczHourViewSet)

urlpatterns = [
  url(r'^$', home, name='home'),
  url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/',
      courts, name='courts'),
  url(r'^auth_login/$', auth_views.login,
      {'template_name': 'users/login.html'}, name='auth_login'),
  url(r'^auth_logout/$', auth_views.logout,
      {'next_page': '/'}, name='auth_logout'),
  url(r'^admin/', admin.site.urls, name='admin'),
  url(r'^', include(router.urls)),
  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

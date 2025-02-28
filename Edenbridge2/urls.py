"""Edenbridge2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import include, path
import info.views
from register import views as v
from register.views import Passwordviewss
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("info.urls")),
    path('', include("schedule.urls")),
    path('', include("booktime.urls")),
    path('', include("django.contrib.auth.urls")),
    path("addstaff", v.register, name="register"),
    path("changepass/", Passwordviewss.as_view(template_name='info/Staff/changepass.html'), name="register"),
    path("modstaff/<str:pk_test>/", v.modstaff, name="modstaff"),
]

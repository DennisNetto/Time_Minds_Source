from django.urls import path
from django.contrib.auth import views as auth_views
import register.views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('land', views.land, name='land'),
    path('land/coordinator', views.cor, name='land-cor'),
    path('land/worker', views.wok, name='land-wok'),
    path('land/bookeeper', views.bok, name='land-bok'),
    path('help', views.help1, name='help'),
    path('about', views.about, name='about'),
    path('viewstaff', views.viewstaff, name='viewstaff'),
    path('addclient', views.addclient, name='addclient'),
    path('viewclient', views.viewclient, name='viewclient'),
    path('modclient/<str:pk_test>/', views.modclient, name='modclient'),
    path('adddep', views.adddep, name='adddep'),
    path('viewdep', views.viewdep, name='viewdep'),
    path('moddep/<str:pk_test>/', views.moddep, name='moddep'),
    path('passuser/<str:pk_test>/', views.changeuserpass, name='passuser'),

]

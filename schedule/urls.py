from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    path('scheduleshift', views.scedshift, name='schedshift'),
    path('viewshift', views.viewshift, name='viweshift'),
    path('viewrecshift', views.viewrecshifts, name='viwerecshift'),
    path('modshift/<str:pk_test>/', views.modshift, name='modshift'),
    path('modrecshift/<str:pk_test>/', views.modrecshift, name='modrecshift'),
    path('approvehours', views.approvehours, name='approvehours'),
    path('approve/<str:pk_test>/', views.approve, name='approve'),
    path('reports', views.reports, name='reports'),



]

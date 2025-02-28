from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('viewscedule', views.workercalender, name='workercalender'),
    path('viewothermonth', views.viewother, name='othermonth'),
    path('timesheet', views.timesheet, name='timesheet'),
    path('shiftdetails/<str:pk_test>/', views.shiftdetails, name='shiftdetails'),
    path('altershift', views.altershift, name='altershift'),
]

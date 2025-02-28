import django_filters
from .models import *
from users.models import Profile


class ClientFilter(django_filters.FilterSet):
    class Meta:
        model = Client
        fields = ['client_id']


class StaffFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = ['staff_id']

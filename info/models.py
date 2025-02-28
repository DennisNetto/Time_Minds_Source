from django.db import models
from users.models import Profile

# Shift statuses
# Approved
# Claimed
# Scheduled
# Cancelled

# Client,Staff,Group Home, and Department Statuses
# Active
# Inactive
# On Hold

# !!!!!!!!!REMEMBER TO MIGRATE APPS YOU NEED TO DO THEM ONE BY ONE NOT JUST IN GENERAL.


class Client(models.Model):
    client_id = models.AutoField(auto_created=True, db_column='CLIENT_ID', primary_key=True)
    client_status = models.CharField(max_length=14, default="Active", db_column='CLIENT_STATUS')
    client_fname = models.CharField(db_column='CLIENT_FNAME', max_length=20)
    client_lname = models.CharField(db_column='CLIENT_LNAME', max_length=20)
    client_phone = models.CharField(db_column='CLIENT_PHONE', max_length=15, blank=True, null=True)
    client_address = models.CharField(db_column='CLIENT_ADDRESS', max_length=50, blank=True, null=True)
    client_city = models.CharField(db_column='CLIENT_CITY', max_length=20, blank=True, null=True)
    client_max_hours = models.IntegerField(db_column='CLIENT_MAX_HOURS', blank=True, null=True)
    client_km = models.IntegerField(db_column='CLIENT_KM', blank=True, null=True)
    client_notes = models.TextField(db_column='CLIENT_NOTES', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'client'


class Department(models.Model):
    dep_code = models.CharField(db_column='DEP_CODE', primary_key=True, max_length=3)
    dep_status = models.CharField(max_length=14, default="Active", db_column='DEP_STATUS')
    dep_name = models.CharField(db_column='DEP_NAME', max_length=30, blank=True, null=True)
    dep_desc = models.CharField(db_column='DEP_DESC', max_length=150, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'department'


class RecShift(models.Model):
    rec_id = models.IntegerField(db_column='REC_ID', primary_key=True)
    dep_code = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='DEP_CODE')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='CLIENT_ID')
    staff = models.ForeignKey(Profile, on_delete=models.CASCADE, db_column='STAFF_ID')
    rec_day = models.CharField(db_column='REC_DAY', max_length=3)
    rec_start = models.TimeField(db_column='REC_START', blank=True, null=True)
    rec_end = models.TimeField(db_column='REC_END', blank=True, null=True)
    rec_super = models.IntegerField(db_column='REC_SUPER', blank=True, null=True)
    rec_notes = models.TextField(db_column='REC_NOTES', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rec_shift'


class Shift(models.Model):
    shift_id = models.AutoField(auto_created=True, db_column='SHIFT_ID', primary_key=True)
    rec = models.ForeignKey(RecShift, on_delete=models.CASCADE, db_column='REC_ID', blank=True, null=True)
    status_code = models.CharField(max_length=14, default="Scheduled", db_column='STATUS_CODE')
    dep_code = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='DEP_CODE')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='CLIENT_ID')
    staff = models.ForeignKey(Profile, on_delete=models.CASCADE, db_column='STAFF_ID')
    shift_date = models.DateField(db_column='SHIFT_DATE')
    scheduled_start = models.TimeField(db_column='SCHEDULED_START', blank=True, null=True)
    scheduled_end = models.TimeField(db_column='SCHEDULED_END', blank=True, null=True)
    claimed_start = models.TimeField(db_column='CLAIMED_START', blank=True, null=True)
    claimed_end = models.TimeField(db_column='CLAIMED_END', blank=True, null=True)
    approved_start = models.TimeField(db_column='APPROVED_START', blank=True, null=True)
    approved_end = models.TimeField(db_column='APPROVED_END', blank=True, null=True)
    shift_super = models.IntegerField(db_column='SHIFT_SUPER', blank=True, null=True)
    shift_notes = models.TextField(db_column='SHIFT_NOTES', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shift'


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.AutoField(db_column='STAFF_ID', primary_key=True)
    type_code = models.CharField(db_column='TYPE_CODE', max_length=13)
    staff_status = models.CharField(db_column='STAFF_STATUS', max_length=10)
    staff_fname = models.CharField(db_column='STAFF_FNAME', max_length=20)
    staff_lname = models.CharField(db_column='STAFF_LNAME', max_length=20)
    staff_phone = models.CharField(db_column='STAFF_PHONE', max_length=15, blank=True, null=True)
    staff_address = models.CharField(db_column='STAFF_ADDRESS', max_length=50, blank=True, null=True)
    staff_city = models.CharField(db_column='STAFF_CITY', max_length=20, blank=True, null=True)
    sun_avail = models.CharField(db_column='SUN_AVAIL', max_length=20, blank=True, null=True)
    mon_avail = models.CharField(db_column='MON_AVAIL', max_length=20, blank=True, null=True)
    tue_avail = models.CharField(db_column='TUE_AVAIL', max_length=20, blank=True, null=True)
    wed_avail = models.CharField(db_column='WED_AVAIL', max_length=20, blank=True, null=True)
    thu_avail = models.CharField(db_column='THU_AVAIL', max_length=20, blank=True, null=True)
    fri_avail = models.CharField(db_column='FRI_AVAIL', max_length=20, blank=True, null=True)
    sat_avail = models.CharField(db_column='SAT_AVAIL', max_length=20, blank=True, null=True)
    staff_notes = models.TextField(db_column='STAFF_NOTES', blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

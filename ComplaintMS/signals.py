# signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile

@receiver(post_save, sender=User, dispatch_uid='save_new_user_profile')
def save_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()

#@receiver(post_save, sender=User, dispatch_uid='save_new_user_profile')
#def save_profile(sender, instance, created, **kwargs):
    #user = instance
    #if created:
        #complaint = Complaint(user=user)
        #complaint.save()
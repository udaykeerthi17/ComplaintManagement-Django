from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import RegexValidator
from datetime import datetime

class Profile(models.Model):
    typeuser = (('student', 'student'), ('grievance', 'grievance'))
    COL = (('College1', 'College1'), ('College2', 'College2'))  # Change college names

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    collegename = models.CharField(max_length=29, choices=COL, blank=False)
    phone_regex = RegexValidator(regex=r'^\d{10,10}$', message="Phone number must be entered in the format: Up to 10 digits allowed.")
    contactnumber = models.CharField(validators=[phone_regex], max_length=10, blank=True)
    type_user = models.CharField(max_length=20, default='student', choices=typeuser)
    CB = (('InformationTechnology', "InformationTechnology"),
          ('ComputerScience', "ComputerScience"),
          ('InformationScience', "InformationScience"),
          ('Electronics and Communication', "Electronics and Communication"),
          ('Mechanical', "Mechanical"))
    Branch = models.CharField(choices=CB, max_length=29, default='InformationTechnology')

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Complaint(models.Model):
    STATUS = ((1, 'Solved'), (2, 'InProgress'), (3, 'Pending'))
    TYPE = (('ClassRoom', "ClassRoom"), ('Teacher', "Teacher"), ('Management', "Management"), ('College', "College"), ('Other', "Other"))

    Subject = models.CharField(max_length=200, blank=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    Type_of_complaint = models.CharField(choices=TYPE, null=True, max_length=200)
    Description = models.TextField(max_length=4000, blank=False, null=True)
    Time = models.DateField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=3)

    def save(self, *args, **kwargs):
        if self.status == 1 and not hasattr(self, 'active_from'):
            self.active_from = datetime.now()
        super(Complaint, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_Type_of_complaint_display()} - {self.Subject}"

class Grievance(models.Model):
    guser = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.guser.username

# Signal to create Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal to save Profile whenever User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

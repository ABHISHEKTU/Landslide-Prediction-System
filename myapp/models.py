from django.db import models 
from django.contrib.auth.models import User

# Create your models here.
class Authority(models.Model):
    USER_ID = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    district = models.CharField(max_length=100)
    place = models.CharField(max_length=100)


class UserProfile(models.Model): 
    USER_ID = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    district = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)

class Complaints(models.Model):   
    USER_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500) 
    date = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)

class AuthorityLandslideReport(models.Model):
    AUTHORITY_ID = models.ForeignKey(Authority, on_delete=models.CASCADE)
    place = models.CharField(max_length=100)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    date=models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='pending')

class EmergencyNotification(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active')

class HelplineNumber(models.Model):   
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

class UserLandslideReport(models.Model):    
    userProfile_ID = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    place = models.CharField(max_length=100)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    date=models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='pending')
    
class FamilyFriendsNumber(models.Model):  
    userprofile_ID = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)       



    def __str__(self):
        return self.name
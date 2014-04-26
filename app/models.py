from django.db import models

class UserInfo(models.Model):
    openId = models.CharField(max_length=50, primary_key=True)
    cardNumber = models.CharField(max_length=20, null=True)
    pcPwd = models.CharField(max_length=30, null=True)
    libUsername = models.CharField(max_length=50, null=True)
    libPwd = models.CharField(max_length=30, null=True)

class Curriculum(models.Model):
    openId = models.CharField(max_length=50, null=True)
    day = models.CharField(max_length=50, null=True)
    courseName = models.CharField(max_length=50, null=True)
    place = models.CharField(max_length=50, null=True)
    period = models.CharField(max_length=50, null=True)
    week = models.CharField(max_length=50, null=True)
    strategy = models.CharField(max_length=50, null=True)
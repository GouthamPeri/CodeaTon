from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from jsonfield import JSONField
from django.contrib.sessions.models import Session
from django.conf import settings
import json


class UserLoginTime(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    login_time = models.CharField(max_length=30)

    def __str__(self):
        return self.user.username


class Questions(models.Model):
    question_code = models.CharField(max_length=10, primary_key=True)
    question_text = models.CharField(max_length=10000)
    question_marks = models.IntegerField()
    input_format = models.CharField(max_length=1000)
    output_format = models.CharField(max_length=1000)
    sample_input = models.CharField(max_length=1000)
    sample_output = models.CharField(max_length=1000)
    constraints = models.CharField(max_length=1000)
    explanation = models.CharField(max_length=3000)


class Status(models.Model):
    team_name = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    status = models.CharField(max_length=10000)
    program_code = models.CharField(max_length=100000)
    time = models.CharField(null=True, blank=True, max_length=1000)
    total_score = models.IntegerField(default=0)
    total_time=models.FloatField(default=0.0)

class Registration(models.Model):
    team_name = models.CharField(max_length=10,primary_key=True)
    member_1_name = models.CharField(max_length=30)
    member_1_phone_no = models.IntegerField()
    member_1_email = models.EmailField(max_length=30)
    member_2_name = models.CharField(max_length=30,null=True,blank=True)
    member_2_phone_no = models.IntegerField(null=True,blank=True)
    member_2_email = models.EmailField(max_length=30,null=True,blank=True)


    #status_obj = Status.objects.get(pk=1)
#status_obj.status = {'name' : 'hello', 'type' : 'text'}
#status_obj.save()
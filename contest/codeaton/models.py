from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from jsonfield import JSONField

class Questions(models.Model):
    question_code = models.CharField(max_length=10, primary_key=True)
    question_text = models.CharField(max_length=10000)
    question_marks = models.IntegerField()


class Status(models.Model):
    team_name = models.OneToOneField(User, primary_key=True)
    status = JSONField(blank=True, null=True)
    code = models.CharField(max_length=100000)

#status_obj = Status.objects.get(pk=1)
#status_obj.status = {'name' : 'hello', 'type' : 'text'}
#status_obj.save()
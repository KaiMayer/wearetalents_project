from django.db import models
from django.contrib.sessions.models import *


class JobPost(models.Model):
    id = models.PositiveIntegerField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    description = models.TextField(max_length=500, default='')
    updated_date = models.DateTimeField()
    location = models.CharField(max_length=50, null=True)
    author = models.CharField(max_length=50)
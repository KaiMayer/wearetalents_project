from django.db import models
from django.utils import timezone


class JobPost(models.Model):
    id = models.PositiveIntegerField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    content = models.TextField(default='', null=True)
    description = models.TextField(max_length=500, default='', null=True)
    author = models.CharField(max_length=50, null=True)
    date_posted = models.DateTimeField(default=timezone.now, null=True)
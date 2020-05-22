from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Poll(models.Model):
    name = models.CharField(max_length=50, default='')
    text = models.CharField(max_length=1000)
    user = models.ForeignKey(User, default=1, on_delete=models.SET_DEFAULT)
    is_checkbox = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


class Option(models.Model):
    text = models.CharField(max_length=500)
    voting = models.ForeignKey(Poll, on_delete=models.PROTECT)


class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    img = models.ImageField(upload_to='voteapp/static/avatars/', default='voteapp/static/avatars/default.png')


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    option = models.ForeignKey(Option, on_delete=models.PROTECT)
    poll = models.ForeignKey(Poll, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    text = models.CharField(max_length=50)
    polls = models.ManyToManyField(Poll, related_name='tag')


class Comment(models.Model):
    text = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    datetime = models.DateTimeField(auto_now=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

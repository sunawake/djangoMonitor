from __future__ import unicode_literals

from django.db import models

# Create your models here.

# for values of region
# | id | name | region id | sub region ids | description |
class Region(models.Model):
    name = models.CharField(max_length=30)
    region_id = models.CharField(max_length=10)
    parent_id = models.CharField(max_length=10)
    description = models.CharField(max_length=200)

# for contents of comment elements
# | id | name | section id | chapter id | page id | description | timeinfo |
class Element(models.Model):
    name = models.CharField(max_length=50)
    section_id = models.CharField(max_length=10)
    chapter_id = models.CharField(max_length=10)
    page_id = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    timesinfo = models.CharField(max_length=10)

# for values of comment elements
# | id | value | region id | section id | chapter id | page id | timestamp | time | description |
class Score(models.Model):
    value = models.CharField(max_length=10)
    region_id = models.CharField(max_length=10)
    section_id = models.CharField(max_length=10)
    chapter_id = models.CharField(max_length=10)
    page_id = models.CharField(max_length=10)
    stat = models.CharField(max_length=10)
    time = models.DateTimeField()
    description = models.CharField(max_length=200)

# for user verification
# | id | username | password | uid |
class User(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    region_id = models.CharField(max_length=10)
    uid = models.CharField(max_length=10)

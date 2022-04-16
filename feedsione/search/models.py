from django.db import models


class Search(models.Model):
    name = models.CharField(max_length=200)
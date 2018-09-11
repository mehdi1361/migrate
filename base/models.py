# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models


# Create your models here.

class Base(models.Model):
    created_date = models.DateTimeField(_('created date'), auto_now_add=True)
    updated_date = models.DateTimeField(_('created date'), auto_now=True)

    class Meta:

        abstract = True




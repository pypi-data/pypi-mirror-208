# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 10:24 AM
# Project:      CFHL Transactional Backend
# Module Name:  dated_model
# Description:
# ****************************************************************
from zibanu.django.db.models.model import Model
from django.db import models
from django.utils.translation import gettext_lazy as _


class DatedModel(Model):
    created_at = models.DateTimeField(blank=False, null=False, verbose_name=_("Created at"), auto_now_add=True)
    modified_at = models.DateTimeField(blank=False, null=False, verbose_name=_("Modified at"), auto_now=True)

    class Meta:
        abstract = True

# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 1:12 PM
# Project:      CFHL Transactional Backend
# Module Name:  apps
# Description:
# ****************************************************************
from django.conf import settings
from django.apps import AppConfig


class ZbDjango(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zibanu.django'
    label = "zb_django"

    def ready(self):
        settings.ZB_MAIL_DEFAULT_FROM = getattr(settings, "ZB_MAIL_DEFAULT_FROM", None)
        settings.ZB_MAIL_REPLY_TO = getattr(settings, "ZB_MAIL_REPLY_TO", None)

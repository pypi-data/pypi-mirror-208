# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/04/23 7:18
# Project:      Django Plugins
# Module Name:  apps
# Description:
# ****************************************************************
from datetime import timedelta
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ZbDjangoAuth(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "zibanu.django.auth"
    verbose_name = _("Zibanu Auth for Django")
    label = "zb_auth"

    def ready(self):
        # Set default settings for Simple JWT Module
        settings.ZB_AUTH_INCLUDE_GROUPS = getattr(settings, "ZB_AUTH_INCLUDE_GROUPS", True)
        settings.ZB_AUTH_INCLUDE_PERMISSIONS = getattr(settings, "ZB_AUTH_INCLUDE_PERMISSIONS", False)

# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/12/22 10:23 AM
# Project:      CFHL Transactional Backend
# Module Name:  apps
# Description:
# ****************************************************************
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ZbDjangoLogging(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "zibanu.django.logging"
    verbose_name = _("Zibanu Logging")
    label = "zb_logging"

    def ready(self):
        # Import events for signals
        import zibanu.django.logging.lib.events

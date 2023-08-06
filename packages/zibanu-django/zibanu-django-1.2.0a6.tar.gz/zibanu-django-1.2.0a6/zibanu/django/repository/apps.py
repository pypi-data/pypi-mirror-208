# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/02/23 16:11
# Project:      CFHL Transactional Backend
# Module Name:  apps
# Description:
# ****************************************************************
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ZbDjangoRepository(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "zibanu.django.repository"
    label = "zb_repository"
    verbose_name = _("Zibanu Django Repository")

    def ready(self):
        settings.ZB_REPOSITORY_DIRECTORY = getattr(settings, "ZB_REPOSITORY_DIRECTORY", "ZbRepository")


# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/12/22 10:27 AM
# Project:      CFHL Transactional Backend
# Module Name:  models
# Description:
# ****************************************************************
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models


class Log(models.DatedModel):
    action = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("Action"))
    sender = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("Sender object method"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"))
    user = models.ForeignKey(get_user_model(), null=True, blank=False, verbose_name=_("User"), on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=("user", ), name="IDX_logging_log_user"),
            models.Index(fields=("action", ), name="IDX_logging_log_action")
        ]


class MailLog(models.Model):
    log = models.OneToOneField(Log, blank=False, null=False, on_delete=models.PROTECT, verbose_name=_("Log"))
    mail_from = models.CharField(max_length=250, blank=False, null=False, verbose_name=_("Mail From"))
    mail_to = models.CharField(max_length=250, blank=False, null=False, verbose_name=_("Mail To"))
    subject = models.CharField(max_length=250, blank=False, null=False, verbose_name=_("Subject"))
    smtp_code = models.IntegerField(blank=False, null=False, verbose_name=_("SMTP Code"), default=0)
    smtp_error = models.CharField(max_length=250, blank=False, null=True, verbose_name=_("SMTP Error"))
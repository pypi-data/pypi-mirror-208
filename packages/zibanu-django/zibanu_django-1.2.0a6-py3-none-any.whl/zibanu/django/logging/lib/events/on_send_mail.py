# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         17/03/23 8:23
# Project:      CFHL Transactional Backend
# Module Name:  on_send_mail
# Description:
# ****************************************************************
import inspect
from django.dispatch import receiver
from zibanu.django.logging.lib.signals import send_mail
from zibanu.django.logging.models import Log
from zibanu.django.logging.models import MailLog


@receiver(send_mail)
def on_send_mail(sender, mail_from: str, mail_to: list, subject: str, smtp_error: str, smtp_code: int, **kwargs):
    class_name = sender.__name__
    log = Log(sender=class_name, action=inspect.currentframe().f_code.co_name)
    log.save()
    mail_log = MailLog(log=log, mail_from=mail_from, mail_to=";".join(mail_to), subject=subject, smtp_error=smtp_error,
                       smtp_code=smtp_code)
    mail_log.save()

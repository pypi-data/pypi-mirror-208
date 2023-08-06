# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 10:36
# Project:      CFHL Transactional Backend
# Module Name:  on_change_password
# Description:
# ****************************************************************
from django.dispatch import receiver
from typing import Any
from zibanu.django.logging.lib.signals import change_password
from zibanu.django.logging.lib.signals import retrieve_password
from zibanu.django.logging.models import Log
from zibanu.django.utils import get_ip_address


@receiver(change_password)
@receiver(retrieve_password)
def on_change_password(sender: Any, user: Any, **kwargs):
    """
    Evento manager for change_password signal
    """
    action = kwargs.get("action", None)
    class_name = sender.__name__
    ip_address = get_ip_address(kwargs.get("request", None))
    log = Log(sender=class_name, action=action, ip_address=ip_address, user=user)
    log.save()
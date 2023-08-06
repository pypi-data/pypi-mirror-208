# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         15/03/23 15:40
# Project:      CFHL Transactional Backend
# Module Name:  on_login
# Description:
# ****************************************************************
import inspect
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from typing import Any
from zibanu.django.logging.models import Log
from zibanu.django.utils import get_ip_address


@receiver(user_logged_in)
def on_login(sender: Any, user: Any, **kwargs):
    """
    Event manager for user_logged_in signal
    """
    class_name = sender.__name__
    # Get action from kwargs
    action = kwargs.get("action", None)
    if action is None:
        action = inspect.currentframe().f_code.co_name
    # Get IP Address from request in kwargs
    ip_address = get_ip_address(kwargs.get("request", None))
    log = Log(sender=class_name, action=action, user=user, ip_address=ip_address)
    log.save()

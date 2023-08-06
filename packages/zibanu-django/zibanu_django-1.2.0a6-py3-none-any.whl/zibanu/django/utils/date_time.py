# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         12/12/22 12:03 PM
# Project:      CFHL Transactional Backend
# Module Name:  date_time
# Description:
# ****************************************************************
from django.utils import timezone
from datetime import datetime
from zoneinfo import ZoneInfo


def change_timezone(date_to_change: datetime, new_timezone: ZoneInfo = None) -> datetime:
    """
    Function for django framework to change a timezone from a datetime var. If timezone is not passed, the function
    will assume a default timezone from django
    :param date_to_change: source datetime var to be changed
    :param new_timezone: a new timezone to be assigned
    :return:
    """
    # If timezone is none, assume default time zone from django
    if new_timezone is None:
        new_timezone = timezone.get_default_timezone()

    try:
        date_to_change = date_to_change.replace(tzinfo=new_timezone)
    except ValueError as exc:
        pass
    except Exception as exc:
        raise Exception from exc
    else:
        return date_to_change


def add_timezone(date_to_change: datetime, tz: ZoneInfo = None) -> datetime:
    """
    Function to assign zone info to datetime if is naive
    :param date_to_change: source datetime var for assign it
    :param tz: timezone to be assigned. If is none, default timezone from django will be used.
    :return:
    """
    if tz is None:
        tz = timezone.get_default_timezone()

    if timezone.is_naive(date_to_change):
        date_to_change = tz.make_aware(date_to_change, timezone=tz)
    return date_to_change

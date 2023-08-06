# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         27/04/23 9:57
# Project:      Zibanu - Django
# Module Name:  decorators
# Description:
# ****************************************************************
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from typing import Any
from zibanu.django.utils import get_user_object


def permission_required(permissions: Any, raise_exception=True):
    """
    Decorator to validate permissions from django auth structure, including JWT authentication
    :param permissions: permission string or tuple with permissions list.
    :param raise_exception: True if you want to raise exception (default), False if not.
    :return: True if successfully
    """
    def check_perms(user):
        """
        Internal function to check perms from master function
        :param user: User object received.
        :return: True if success, False otherwise.
        """
        b_return = False
        local_user = get_user_object(user)

        # Build perms list
        if isinstance(permissions, str):
            perms = (permissions,)
        else:
            perms = permissions

        if local_user.has_perms(perms) or local_user.is_superuser:
            b_return = True
        elif raise_exception:
            raise PermissionDenied(_("You do not have permission to perform this action."), "not_authorized")
        return b_return
    return user_passes_test(check_perms)
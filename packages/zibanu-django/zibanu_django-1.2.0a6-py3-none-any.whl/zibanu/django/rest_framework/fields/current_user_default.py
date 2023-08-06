# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         30/03/23 14:58
# Project:      Biodiversity Backend
# Module Name:  current_user_default
# Description:
# ****************************************************************
from rest_framework.serializers import CurrentUserDefault as SourceCurrentUserDefault
from zibanu.django.utils import get_user
from typing import Any

class CurrentUserDefault(SourceCurrentUserDefault):
    """
    Override default class CurrentUserDefault
    """
    def __call__(self, serializer_field) -> Any:
        """
        Default call method
        :param serializer_field: field received from serializer
        :return:
        """
        local_user = None
        if "request" in serializer_field.context.keys():
            local_user = get_user(serializer_field.context.get("request"))
        return local_user

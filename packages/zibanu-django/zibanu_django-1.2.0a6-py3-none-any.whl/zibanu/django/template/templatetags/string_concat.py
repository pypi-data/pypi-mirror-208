# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/02/23 18:56
# Project:      CFHL Transactional Backend
# Module Name:  string_concat
# Description:
# ****************************************************************
from django import template

register = template.Library()


@register.simple_tag
def string_concat(first_string: str, *args):
    return first_string % args


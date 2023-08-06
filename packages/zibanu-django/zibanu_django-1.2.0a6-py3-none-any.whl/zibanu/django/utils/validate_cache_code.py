# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         3/03/23 8:19
# Project:      CFHL Transactional Backend
# Module Name:  validate_cache_code
# Description:
# ****************************************************************
from django.core.cache import cache
from typing import Any


def validate_cache_code(cache_key: str, code: str, code_key: str = None):
    if code_key is None:
        code_key = "code"


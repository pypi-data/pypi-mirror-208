# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 10:14 AM
# Project:      CFHL Transactional Backend
# Module Name:  __init__.py
# Description:
# ****************************************************************
from django.db.models import *
from .manager import Manager
from .model import Model
from .dated_model import DatedModel
from django.db.models import __all__ as models_all

__all__ = models_all

__all__ += [
    "DatedModel",
    "Manager",
    "Model"
]



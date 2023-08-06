# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 10:14 AM
# Project:      CFHL Transactional Backend
# Module Name:  base_model
# Description:
# ****************************************************************
from django.db import models


class Model(models.Model):
    """
    Base class to create new models with standard fields and save
    """
    # Protected attribute
    use_db = "default"

    class Meta:
        abstract = True

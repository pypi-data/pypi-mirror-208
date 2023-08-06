# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/02/23 15:45
# Project:      CFHL Transactional Backend
# Module Name:  document
# Description:
# ****************************************************************
from zibanu.django.db import models


class Document(models.Manager):
    def get_by_uuid(self, uuid: str):
        return self.filter(uuid__exact=uuid)

    def get_by_code(self, code: str):
        return self.filter(code__exact=code)


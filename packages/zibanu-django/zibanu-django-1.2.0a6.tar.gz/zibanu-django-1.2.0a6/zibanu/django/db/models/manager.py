# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         14/12/22 5:21 AM
# Project:      CFHL Transactional Backend
# Module Name:  manager
# Description:
# ****************************************************************
from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _


class Manager(models.Manager):
    """
    Override class from models.Manager
    """
    def get_queryset(self) -> models.QuerySet:
        """
        Override method to get a default queryset for a model, setting using from "use_db" model Meta class attribute.
        :return: queryset for a model.
        """
        qs = super().get_queryset()
        if hasattr(self.model, "use_db"):
            qs = qs.using(self.model.use_db)
        return qs

    def get_by_pk(self, pk: Any) -> models.QuerySet:
        """
        Method to get a queryset filtered by pk
        :param pk: primary key
        :return:
        """
        # Validate if pk key exists
        qs = self.get_queryset().filter(pk=pk)
        if len(qs) == 0:
            raise self.model.DoesNotExist(_("OASIS Error. The object does not exists."))
        return qs

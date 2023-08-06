# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/02/23 16:13
# Project:      CFHL Transactional Backend
# Module Name:  models
# Description:
# ****************************************************************
import uuid
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models
from zibanu.django.repository.lib import managers


class Document(models.Model):
    """
    Model class that represent a document entity in database
    """
    code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Validation Code"))
    uuid = models.UUIDField(default=uuid.uuid4, verbose_name=_("UUID File"))
    owner = models.ForeignKey(get_user_model(), verbose_name=_("Owner"), on_delete=models.PROTECT)
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Generated At"))
    description = models.CharField(max_length=150, blank=False, null=False, verbose_name=_("Description"), default="")
    # Set default Manager
    objects = managers.Document()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("code", ), name="UNQ_documents_code"),
            models.UniqueConstraint(fields=("uuid", ), name="UNQ_documents_uuid")
        ]




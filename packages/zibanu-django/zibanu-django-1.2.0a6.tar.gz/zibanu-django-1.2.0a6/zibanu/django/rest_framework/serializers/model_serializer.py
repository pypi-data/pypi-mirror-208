# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 3:33 PM
# Project:      CFHL Transactional Backend
# Module Name:  model_serializer
# Description:
# ****************************************************************
from rest_framework.serializers import ModelSerializer as SourceModelSerializer
from rest_framework.fields import empty


class ModelSerializer(SourceModelSerializer):
    """
    Override class for ModelSerializer
    """
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)

    
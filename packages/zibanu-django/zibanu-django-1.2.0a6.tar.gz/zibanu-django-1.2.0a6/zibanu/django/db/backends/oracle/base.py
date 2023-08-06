# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/02/23 20:30
# Project:      CFHL Transactional Backend
# Module Name:  base
# Description:
# ****************************************************************
from django.db.backends.utils import truncate_name
from django.db.backends.oracle.base import DatabaseWrapper as OracleWrapper
from django.db.backends.oracle.operations import DatabaseOperations as OracleOperations


class DatabaseOperations(OracleOperations):
    def format_for_duration_arithmetic(self, sql):
        super().format_for_duration_arithmetic(sql=sql)

    def quote_name(self, name):
        if not name.startswith('"') and not name.endswith('"'):
            name = '"%s"' % truncate_name(name.upper(), self.max_name_length())
        return name.replace("%", "%%")


class DatabaseWrapper(OracleWrapper):
    ops_class = DatabaseOperations


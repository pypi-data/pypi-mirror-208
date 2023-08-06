# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         14/12/22 4:14 AM
# Project:      CFHL Transactional Backend
# Module Name:  api_exception
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException as SourceException
from rest_framework import status


class APIException(SourceException):
    """
    Override class from APIException
    """
    __default_messages = {
        "304": _("Object has not been created."),
        "400": _("Generic error."),
        "401": _("You are not authorized for this resource."),
        "403": _("You do not have permission to perform this action."),
        "404": _("Object does not exists."),
        "406": _("Data validation error."),
        "412": _("Data required not found."),
        "500": _("Not controlled exception error."),
    }

    def __init__(self, msg: str = None, error: str = None, http_status: int = status.HTTP_400_BAD_REQUEST) -> None:
        """
        Override init method
        :param msg: list, dict, str: Data to show the exception detail.
        :param error: list,dict, str: Code error
        :param http_status: int: Status code
        """
        str_status = str(http_status)

        # Define default messages if args not passed
        error = error if error is not None else _("Generic error.")
        msg = msg if msg is not None else self.__default_messages.get(str_status, _("Generic error."))

        # Create detail dictionary
        detail = {
            "message": msg,
            "detail": error
        }

        if http_status is not None:
            self.status_code = http_status

        super().__init__(detail)



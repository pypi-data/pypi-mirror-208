# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 15:37
# Project:      CFHL Transactional Backend
# Module Name:  site
# Description:
# ****************************************************************
def site(request):
    """
    Template context processors for get absolute site uri
    :param request: request object from HTTP
    :return: string with absolute uri
    """
    return {
        "site": request.build_absolute_uri("/")
    }

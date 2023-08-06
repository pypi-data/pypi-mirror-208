# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 10:42
# Project:      CFHL Transactional Backend
# Module Name:  request_utils
# Description:
# ****************************************************************
from typing import Any
def get_ip_address(request:Any) -> str:
    """
    Get ip Address from request
    """
    ip_address = None
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR")
    return ip_address
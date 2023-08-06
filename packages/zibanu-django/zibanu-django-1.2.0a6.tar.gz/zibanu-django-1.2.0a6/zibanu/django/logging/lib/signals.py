# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 10:36
# Project:      CFHL Transactional Backend
# Module Name:  signals
# Description:
# ****************************************************************
from django import dispatch

change_password = dispatch.Signal()
retrieve_password = dispatch.Signal()
send_mail = dispatch.Signal()
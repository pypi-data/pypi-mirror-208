# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/04/23 7:32
# Project:      Django Plugins
# Module Name:  urls
# Description:
# ****************************************************************
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainSlidingView
from rest_framework_simplejwt.views import TokenRefreshSlidingView
from zibanu.django.auth.api.services import UserService

urlpatterns = [
    path("login/", TokenObtainSlidingView.as_view(), name="token_obtain"),
    path("refresh/", TokenRefreshSlidingView.as_view(), name="token_refresh"),
    path("user/list/", UserService.as_view({"post": "list"}), name="list_users"),
    path("user/add/", UserService.as_view({"post": "create"}), name="add_user")
]
# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         27/04/23 6:58
# Project:      Zibanu - Django
# Module Name:  profile
# Description:
# ****************************************************************
from rest_framework import serializers
from zibanu.django.auth.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for UserProfile entity in zibanu library.
    """

    class Meta:
        """
        Profile Serializer Meta Class
        """
        model = UserProfile
        fields = ("timezone", "theme", "lang", "avatar", "messages_timeout", "keep_logged_in", "app_profile")
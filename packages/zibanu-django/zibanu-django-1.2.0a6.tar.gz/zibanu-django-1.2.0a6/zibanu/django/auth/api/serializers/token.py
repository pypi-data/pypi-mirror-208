# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         27/04/23 7:02
# Project:      Zibanu - Django
# Module Name:  token
# Description:
# ****************************************************************
from .user import UserSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import SlidingToken
from typing import Dict, Any


class EmailTokenObtainSerializer(TokenObtainSerializer):
    """
    Class to obtain SimpleJWT token with full user payload, based on email authentication.
    """
    username_field = get_user_model().EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    @classmethod
    def get_token(cls, user):
        """
        Class Method to get token from user object
        :param user: current user object
        :return: token object
        """
        token = super().get_token(user)

        # Include user data
        user_serializer = UserSerializer(instance=user)
        token["user"] = user_serializer.data

        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        """
        Method to validate attributes from request
        :param attrs: attributes sended by request to make authentication
        :return: empty dict
        """
        user = get_user_model().objects.filter(email__iexact=attrs.get(self.username_field)).first()

        if user is None:
            raise AuthenticationFailed(self.error_messages["no_active_account"], "no_active_account")

        authenticate_kwargs = {
            get_user_model().USERNAME_FIELD: user.get_username(),
            "password": attrs.get("password")
        }
        self.user = authenticate(**authenticate_kwargs)
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        return {}


class EmailTokenObtainSlidingSerializer(EmailTokenObtainSerializer):
    """
    Class to obtain Email Token Sliding
    """
    token_class = SlidingToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        """
        Method to validate and generate token from request attributes data
        :param attrs: attributes for authentication process
        :return: dictionary with token auth string
        """
        data = super().validate(attrs)
        token = self.get_token(self.user)
        data["token"] = str(token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data

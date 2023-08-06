# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/04/23 18:17
# Project:      Zibanu - Django
# Module Name:  user
# Description:
# ****************************************************************
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from zibanu.django.auth.api import serializers
from zibanu.django.utils import ErrorMessages
from zibanu.django.rest_framework.exceptions import APIException
from zibanu.django.rest_framework.exceptions import ValidationError
from zibanu.django.rest_framework.decorators import permission_required
from zibanu.django.rest_framework.viewsets import ModelViewSet


class UserService(ModelViewSet):
    model = get_user_model()
    serializer_class = serializers.UserListSerializer

    @method_decorator(permission_required("auth.view_user"))
    def list(self, request, *args, **kwargs) -> Response:
        """
        Override method to add a permission required for list user
        :param request: HTTP request object
        :param args: args for list method
        :param kwargs: kwargs for list method
        :return: response with list
        """
        kwargs = dict({"order_by": "first_name", "is_active__exact": True})
        return super().list(request, *args, **kwargs)

    @method_decorator(permission_required(["auth.add_user", "zb_auth.add_userprofile"]))
    def create(self, request, *args, **kwargs) -> Response:
        try:
            if request.data is not None and len(request.data) > 0:
                # TODO: Add roles and permissions on list.
                roles_data = request.data.pop("roles", [])
                permissions_data = request.data.pop("permissions", [])
                try:
                    transaction.set_autocommit(False)
                    serializer = serializers.UserSerializer(data=request.data)
                    if serializer.is_valid(raise_exception=True):
                        created_user = serializer.create(validated_data=serializer.validated_data)
                        if created_user is not None:
                            pass
                except ValidationError as exc:
                    transaction.rollback()
                    raise
                except Exception as exc:
                    transaction.rollback()
                    raise APIException(ErrorMessages.NOT_CONTROLLED, str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
                else:
                    transaction.commit()
                finally:
                    transaction.set_autocommit(True)

            else:
                raise ValidationError(ErrorMessages.DATA_REQUEST_NOT_FOUND, "request_not_found")
        except ValidationError as exc:
            raise APIException(exc.detail[0], http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc

        return super().create(request, *args, **kwargs)
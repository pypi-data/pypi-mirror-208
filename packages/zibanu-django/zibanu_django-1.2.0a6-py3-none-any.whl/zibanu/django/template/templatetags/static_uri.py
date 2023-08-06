# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 15:33
# Project:      CFHL Transactional Backend
# Module Name:  static_uri
# Description:
# ****************************************************************
from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _

register = template.Library()


class StaticNodeUri(template.Node):
    def __init__(self, uri_string: str):
        self._static_uri = uri_string

    def render(self, context):
        if hasattr(context, "request"):
            request = context.get("request")
            if hasattr(settings, "STATIC_URL"):
                uri = request.build_absolute_uri(settings.STATIC_URL)
                uri = uri + self._static_uri
            else:
                raise template.TemplateSyntaxError(_("'STATIC_URL' setting is not defined."))
        else:
            raise template.TemplateSyntaxError(_("Tag 'static_uri' requires 'request' var in context."))
        return uri


@register.tag("static_uri")
def static_uri(parse, token):
    try:
        tag_name, uri_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("")

    return StaticNodeUri(uri_string[1:-1])




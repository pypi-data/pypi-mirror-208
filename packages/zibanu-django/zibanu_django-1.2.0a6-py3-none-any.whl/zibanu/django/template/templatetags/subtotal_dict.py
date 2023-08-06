# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/02/23 9:03
# Project:      CFHL Transactional Backend
# Module Name:  subtotal_dict
# Description:
# ****************************************************************
from django import template
from django.utils.translation import gettext_lazy as _


register = template.Library()


@register.simple_tag
def subtotal_dict(source_list: list, key_control: str, *args) -> list:
    if args is not None:
        key_value = None
        return_list = []
        item_dict = {
            "control": None,
            "totals": dict(),
            "data": []
        }

        for item in source_list:
            data_dict = dict()
            if key_value is None or key_value != item[key_control]:
                # Add Control var and dict
                if key_value is not None:
                    return_list.append(item_dict)
                key_value = item[key_control]
                # Init vars on change key_value
                item_dict = {
                    "control": item[key_control],
                    "totals": dict(),
                    "data": []
                }
                for param in args:
                    item_dict["totals"][param] = 0

            for key_item in item.keys():
                if key_item != key_control:
                    data_dict[key_item] = item.get(key_item)

                if key_item in item_dict.get("totals").keys():
                    item_dict["totals"][key_item] += item[key_item]

            item_dict["data"].append(data_dict)
        return_list.append(item_dict)
    else:
        raise template.TemplateSyntaxError(_("The keys for subtotals are required."))

    return return_list




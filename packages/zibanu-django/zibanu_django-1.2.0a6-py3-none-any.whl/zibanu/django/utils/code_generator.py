# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/01/23 1:47 PM
# Project:      CFHL Transactional Backend
# Module Name:  code_generator
# Description:
# ****************************************************************
import os
import string
import secrets
from django.utils.translation import gettext_lazy as _
from uuid import SafeUUID, UUID


class CodeGenerator:
    """
    Class to generate random different types of codes
    """
    def __init__(self, action: str, is_safe: SafeUUID = SafeUUID.safe, code_length: int = 6):
        """
        Constructor Method
        :param action: action code to reference it
        :param is_safe: flag to enable SafeUUID
        :param code_length: length of generated code
        """
        self._action = action
        self._is_safe = is_safe
        self._code_length = code_length
        self._code = None
        self._token = None
        self._uuid = None

    @property
    def is_safe(self):
        return self._is_safe

    @is_safe.setter
    def is_safe(self, value: SafeUUID):
        self._is_safe = value

    @property
    def code(self) -> int:
        return self._code

    @property
    def action(self) -> str:
        return self._action

    @action.setter
    def action(self, value: str = None):
        self._action = value

    def _get_uuid(self):
        return UUID(bytes=os.urandom(16), version=4, is_safe=self.is_safe)

    def _get_numeric_code(self):
        return "".join(secrets.choice(string.digits) for i in range(self._code_length))

    def _get_alpha_numeric_code(self):
        return "".join(secrets.choice(string.digits+string.ascii_letters) for i in range(self._code_length))

    def _get_secure_code(self):
        return "".join(secrets.choice(string.digits+string.ascii_letters+string.punctuation) for i in range(self._code_length))

    def generate_numeric_code(self) -> bool:
        try:
            self._code = self._get_numeric_code()
        except Exception:
            return False
        else:
            return True

    def get_numeric_code(self, length: int = None):
        if length is not None:
            self._code_length = length
        return self._get_numeric_code()

    def get_alpha_numeric_code(self, length: int = None):
        if length is not None:
            self._code_length = length
        self._code = self._get_alpha_numeric_code()
        return self.code

    def get_secure_code(self, length: int = None):
        if length is not None:
            self._code_length = length
        self._code = self._get_secure_code()
        return self.code

    def generate_uuid(self) -> bool:
        try:
            self._uuid = self._get_uuid()
        except Exception:
            return False
        else:
            return True

    def generate_dict(self):
        if self.generate_uuid() and self.generate_numeric_code():
            return {"uuid": self._uuid, "code": self._code, "action": self.action}
        else:
            raise ValueError(_("The generated values are invalid."))

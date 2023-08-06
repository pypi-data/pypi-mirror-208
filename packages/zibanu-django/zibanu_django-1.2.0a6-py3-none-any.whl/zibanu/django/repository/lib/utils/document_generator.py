# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         2/02/23 16:27
# Project:      CFHL Transactional Backend
# Module Name:  document_generator
# Description:
# ****************************************************************
import os
import uuid
from datetime import date
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.template.exceptions import TemplateDoesNotExist
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from xhtml2pdf import pisa
from zibanu.django.repository.models import Document


class DocumentGenerator:
    def __init__(self, template_prefix: str, custom_dir: str = None, file_uuid: str = None):
        self.__custom_dir = custom_dir
        self.__template_prefix = template_prefix
        self.__description = ""
        self.__generated = None

        if not template_prefix.endswith("/"):
            self.__template_prefix += "/"

        if template_prefix.startswith("/"):
            self.__template_prefix = self.__template_prefix[1:]

        if hasattr(settings, "MEDIA_ROOT"):
            self.__directory = self.__get_directory()
        else:
            raise ValueError(_("The 'MEDIA_ROOT' setting has not been defined."))

    @property
    def description(self):
        return self.__description

    @property
    def generated_at(self):
        return self.__generated

    def __get_directory(self, **kwargs) -> str:
        """
        Private method to get the path from document, year/month or none parameters
        :param kwargs: dictionary with parameters "document", ("year", "month")
        :return: str to represent path
        """
        year = date.today().year
        month = date.today().month

        if hasattr(settings, "MEDIA_ROOT"):
            if self.__custom_dir is None:
                directory = os.path.join(settings.MEDIA_ROOT, settings.ZB_REPOSITORY_DIRECTORY)
            else:
                directory = os.path.join(settings.MEDIA_ROOT, self.__custom_dir)
        else:
            raise ValueError(_("The 'MEDIA_ROOT' setting has not been defined."))

        if kwargs is not None:
            if "document" in kwargs and isinstance(kwargs.get("document"), Document):
                document = kwargs.get("document")
                year = document.generated_at.year
                month = document.generated_at.month
            elif {"year", "month"} <= kwargs.keys():
                year = kwargs.get("year")
                month = kwargs.get("month")

        directory = os.path.join(directory, str(year))
        directory = os.path.join(directory, str(month))
        return directory

    def __get_qs(self, kwargs):
        if "uuid" in kwargs:
            document_qs = Document.objects.get_by_uuid(kwargs.get("uuid"))
        elif "code" in kwargs:
            document_qs = Document.objects.get_by_code(kwargs.get("code"))
        else:
            raise ValueError(_("Key to get document does not found."))
        return document_qs

    def generate_from_template(self, template_name: str, context: dict, request: HttpRequest, description: str = "",
                               key: str = "code"):
        """
        Method to generate a pdf based on html django template
        :param template_name: name of template to render
        :param context: context file to render template
        :param request: request object from HTTP
        :param description: Description of document
        :param key: key that contains a validation code, default = "code"
        :return:
        """
        try:
            # Created directory if it does not exist
            directory = self.__get_directory()
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Set key to get validation code and get it
            validation_code = context.get(key) if key in context else None
            # Set uuid for filename and uuid file
            file_uuid = uuid.uuid4()
            # Set filename with path and uuid and create it
            file_name = os.path.join(self.__get_directory(), file_uuid.hex + ".pdf")
            # TODO: Validate template name
            # Load template and render it
            template_name = self.__template_prefix + template_name
            template = get_template(template_name)
            rendered = template.render(context=context, request=request)
            # Generate pdf
            file_handler = open(file_name, "w+b")
            pisa_status = pisa.CreatePDF(rendered, file_handler)
            if not pisa_status.err:
                document = Document(code=validation_code, uuid=file_uuid, owner=request.user, description=description)
                document.save()
                file_handler.close()
            else:
                file_handler.close()
                os.remove(file_name)
                raise Exception(_("Error generating pdf file"))
        except OSError:
            raise OSError(_("The file cannot be created."))
        except TemplateDoesNotExist:
            raise TemplateDoesNotExist(_("Template %s does not exist." % template_name))
        except TemplateSyntaxError:
            raise TemplateSyntaxError(_("Syntax error in the template %s") % template_name)
        else:
            return file_uuid.hex

    def get_file(self, user, **kwargs):
        """
        Return a file path+name from user and uuid or code
        :param user: user object from request or simplejwt
        :param kwargs: dict of parameters, uuid or code
        :return: document file name and path
        """
        if user is None:
            raise ValueError(_("User is required"))

        document_qs = self.__get_qs(kwargs)

        if document_qs.count() > 0:
            document = document_qs.first()
            self.__description = document.description
            self.__generated = document.generated_at
            if user == document.owner:
                document_file = os.path.join(self.__get_directory(document=document), document.uuid.hex + '.pdf')
                if not os.path.exists(document_file):
                    raise ObjectDoesNotExist(_("Document file does not exist."))
            else:
                raise ValidationError(_("User does not have permissions to get this document."))
        else:
            raise ObjectDoesNotExist(_("Document does not exist."))
        return document_file

    def get_document(self, **kwargs):
        return self.__get_qs(kwargs).first()


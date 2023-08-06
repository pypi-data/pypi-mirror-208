# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast_vendor.wrapt import register_post_import_hook

from contrast.agent.policy import patch_manager
from contrast.utils.patch_utils import build_and_apply_patch

DJANGO_WSGI_NAME = "django.core.wsgi"


def build_get_wsgi_app_patch(orig_func, patch_policy):
    del patch_policy

    def get_wsgi_application(*args, **kwargs):
        # Avoids circular import
        from contrast.agent.agent_state import set_detected_framework
        from contrast.django import ContrastMiddleware

        # This call needs to occur before middleware initialization
        set_detected_framework("django")

        return ContrastMiddleware(orig_func(*args, **kwargs))

    return get_wsgi_application


def patch_django_wsgi(module):
    build_and_apply_patch(module, "get_wsgi_application", build_get_wsgi_app_patch)


def register_patches():
    register_post_import_hook(patch_django_wsgi, DJANGO_WSGI_NAME)


def reverse_patches():  # pragma: no cover
    patch_manager.reverse_module_patches_by_name(DJANGO_WSGI_NAME)

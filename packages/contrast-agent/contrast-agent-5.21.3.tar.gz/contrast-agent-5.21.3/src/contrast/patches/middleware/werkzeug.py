# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast_vendor.wrapt import register_post_import_hook

from contrast.agent.policy import patch_manager
from contrast.utils.patch_utils import build_and_apply_patch
from contrast.utils.decorators import fail_loudly


WERKZEUG_SERVING_NAME = "werkzeug.serving"


@fail_loudly("Failed to wrap flask middleware")
def wrap_middleware_args(middleware_cls, args):
    """
    Extract application from arguments and wrap with middleware

    Decorator ensures that None will be returned if any problem occurs
    """
    app = args[2]
    if not isinstance(app, middleware_cls):
        app = middleware_cls(app)
        args = args[:2] + (app,) + args[3:]
    return args


def build_make_server_patch(orig_func, patch_policy):
    # Avoids circular import
    from contrast.flask.middleware import FlaskMiddleware

    del patch_policy  # unused

    def make_server(*args, **kwargs):
        from contrast.agent.agent_state import set_detected_framework

        # This call needs to occur before middleware initialization
        set_detected_framework("flask")

        args = wrap_middleware_args(FlaskMiddleware, args) or args
        return orig_func(*args, **kwargs)

    return make_server


def patch_werkzeug_serving(module):
    build_and_apply_patch(module, "make_server", build_make_server_patch)


def register_patches():
    register_post_import_hook(patch_werkzeug_serving, WERKZEUG_SERVING_NAME)


def reverse_patches():
    patch_manager.reverse_module_patches_by_name(WERKZEUG_SERVING_NAME)

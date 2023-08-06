# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import gc
import inspect

from contrast.assess_extensions.cs_str import has_funchook
from contrast.agent import scope
from contrast.agent.assess.policy import string_propagation
from contrast.agent.policy import patch_manager
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch
from contrast.utils.namespace import Namespace


class module(Namespace):
    patched_classes = []


def find_str_subclasses():
    """
    Digs through the garbage (collector) to find any subclasses of str
    """
    for obj in gc.get_objects():
        try:
            if inspect.isclass(obj) and issubclass(obj, (str, bytes)):
                yield obj
        except Exception:
            continue


@fail_quietly("Failed to propagate string subclass __new__")
def propagate_str_cast(result, args, kwargs):
    with scope.contrast_scope():
        string_propagation.propagate_unicode_cast(
            result, args[0], result, args[1:], kwargs
        )


@fail_quietly("Failed to propagate bytes subclass __new__")
def propagate_bytes_cast(result, args, kwargs):
    with scope.contrast_scope():
        string_propagation.propagate_bytes_cast(
            result, args[0], result, args[1:], kwargs
        )


def build_cast_patch(orig_func, patch_policy, propagation_func):
    del patch_policy

    def __new__(*args, **kwargs):
        result = orig_func(*args, **kwargs)
        propagation_func(result, args, kwargs)
        return result

    return __new__


@fail_quietly("Failed to apply patches for string subclasses")
def register_patches():
    """
    Applies patches to known subclasses of str

    Problem statement: the cast/new hook for subclasses of str does not work
    without funchook. This seems to be an issue with timing: subclasses that
    are defined *after* our (non-funchook) extension hooks are applied do not
    appear to have a problem.

    However, even with the runner, our instrumentation is not necessarily going
    to be early enough to affect *all* subclasses that are defined.

    The solution is to use the garbage collector to find any subclasses of str
    that may already be defined at this point in time. We then explicitly apply
    propagation patches to the __new__ methods of these classes.
    """
    if has_funchook():
        return

    for cls in find_str_subclasses():
        propagation_func = None

        if issubclass(cls, str):
            propagation_func = propagate_str_cast
        elif issubclass(cls, bytes):
            propagation_func = propagate_bytes_cast

        if propagation_func is not None:
            build_and_apply_patch(
                cls, "__new__", build_cast_patch, builder_args=(propagation_func,)
            )
            module.patched_classes.append(cls)


def reverse_patches():
    for cls in module.patched_classes:
        patch_manager.reverse_patches_by_owner(cls)

    module.patched_classes = []

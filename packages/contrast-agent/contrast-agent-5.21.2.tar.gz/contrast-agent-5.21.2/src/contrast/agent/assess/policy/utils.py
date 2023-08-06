# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast_vendor import structlog as logging

logger = logging.getLogger("contrast")

CONTRAST_ASSESS_METHOD_START = "cs__assess_"


def build_method_name(method_name):
    """
    Builds a name based on the method name

    Example:
        cs__assess_append
    """
    return CONTRAST_ASSESS_METHOD_START + method_name

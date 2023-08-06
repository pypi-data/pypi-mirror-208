# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os

from contrast_rewriter import REWRITE_FOR_PYTEST
from contrast.patches import register_middleware_patches


def start_runner():
    if os.environ.get(REWRITE_FOR_PYTEST):
        return

    register_middleware_patches()

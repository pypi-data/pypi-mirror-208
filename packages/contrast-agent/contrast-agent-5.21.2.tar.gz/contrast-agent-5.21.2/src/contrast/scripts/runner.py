# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

from argparse import ArgumentParser
import os
import sys
import warnings

# We'll need to extern this function or investigate replacing it with shutil.which()
# "distutils is deprecated with removal planned for Python 3.12. See the What’s
# New entry for more information."
with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        "The distutils package is deprecated and slated for removal in Python 3.12. Use setuptools or check PEP 632 for potential alternatives",
        DeprecationWarning,
    )

    from distutils.spawn import find_executable  # pylint: disable=deprecated-module

from contrast import __file__
from contrast.configuration import AgentConfig
from contrast_rewriter import ENABLE_REWRITER, REWRITE_FOR_PYTEST


def runner() -> None:
    parser = ArgumentParser()
    parser.add_argument("--rewrite-for-pytest", action="store_true")
    parser.add_argument("args", nargs="+")

    parsed = parser.parse_args()

    config = AgentConfig()

    loader_path = os.path.join(os.path.dirname(__file__), "loader")
    os.environ["PYTHONPATH"] = os.path.pathsep.join([loader_path] + sys.path)

    if parsed.rewrite_for_pytest:
        os.environ[REWRITE_FOR_PYTEST] = "true"
    elif config.should_rewrite:
        os.environ[ENABLE_REWRITER] = "true"

    os.execl(find_executable(parsed.args[0]), *parsed.args)

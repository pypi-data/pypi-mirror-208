# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

"""
The sitecustomize.py file is automatically loaded by Python during interpreter initialization.

Our runner script ensures that it is on the PYTHONPATH which is sufficient to make sure it is loaded.

See https://docs.python.org/3/library/site.html for additional details
"""
import contrast_rewriter

# NOTE: This must be applied prior to importing the agent itself
contrast_rewriter.register()


from contrast.agent.runner import start_runner

start_runner()

# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import ast
import importlib
import inspect
import sys
import textwrap
from types import FunctionType, ModuleType

from contrast.agent.policy import patch_manager
from contrast.agent.settings import Settings
from contrast.agent.assess.policy.utils import CONTRAST_ASSESS_METHOD_START
from contrast.agent.policy.patch_manager import reverse_module_patches_by_name
from contrast.utils.decorators import fail_quietly
from contrast_rewriter import PropagationRewriter, populate_operator_module
from contrast_vendor import structlog as logging

# NOTE: it feels like overkill to store this in the policy registry right now,
# but we can always change this later if necessary.
REWRITE_MODULES = [
    "posixpath",
    "urllib.parse",
]

logger = logging.getLogger("contrast")


def get_or_load_module(module: ModuleType) -> ModuleType:
    """
    Returns a non-frozen version of the given module

    Frozen modules are modules whose bytecode is built into the interpreter
    itself for performance reasons. All of the modules required at interpreter
    startup are frozen in newer versions of Python (i.e. >= 3.10+).

    Frozen modules do not have access to the source code of module members such
    as functions. This means that calls to inspect.getsource(<frozen-module-name>.<member-name>)
    will fail. Since we need the source in order to perform rewrites, we need a
    non-frozen version of the module. We can achieve this by loading the module
    again and returning the new module object.
    """
    if module.__loader__ is not importlib.machinery.FrozenImporter:
        return module

    temp_name = "__contrast_temp." + module.__name__
    spec = importlib.util.spec_from_file_location(temp_name, module.__file__)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert temp_name not in sys.modules

    return module


@fail_quietly("Failed to apply rewrites to function")
def rewrite_function(module: ModuleType, name: str, source: str):
    """
    Rewrites the function defined in the given module

    The process invovles the following steps:
    1. Retrieve the source for the given function. (This may fail if the function is defined in an extension)
    2. Generate an AST from the original source code
    3. Transform the AST using our PropagationRewriter
    4. Compile the new AST into a code object
    5. Evaluate the new code object with exec
    6. Retrieve the newly defined function from the locals of the exec call
    """
    filename = module.__file__ or "<unknown>"
    mode = "exec"

    old_ast = ast.parse(textwrap.dedent(source), filename=filename, mode=mode)

    rewriter = PropagationRewriter()
    new_ast = ast.fix_missing_locations(rewriter.visit(old_ast))

    locals_ = {}
    new_code = compile(new_ast, filename, mode=mode)
    exec(new_code, module.__dict__, locals_)

    return locals_[name]


@fail_quietly("Failed rewrite and patch function")
def rewrite_and_patch_function(
    module: ModuleType, name: str, function: FunctionType, source: str
):
    # Some functions may already be patched by other policy, in which case we do not want to rewrite them
    if patch_manager.is_patched(function):
        logger.debug("Skipping rewrite of already patched function: %s", name)
        return

    new_func = rewrite_function(module, name, source)
    if new_func is None:
        logger.debug("No new function for %s. Skipping patch", name)
        return

    patch_manager.patch(module, name, new_func)


@fail_quietly("Failed to rewrite functions for module")
def rewrite_module_functions(module_name: str):
    module = sys.modules.get(module_name, None)
    if module is None:
        logging.debug(
            'Failed to rewrite functions in module "%s": module not loaded', module_name
        )
        return

    logger.debug("Applying rewriter policy to module: %s", module_name)

    populate_operator_module(module.__dict__)

    temp_module = get_or_load_module(module)

    for name, function in [
        (name, member)
        for name, member in inspect.getmembers(module)
        if inspect.isfunction(member)
    ]:
        # TODO: PYT-2823 remove this workaround
        if name.startswith(CONTRAST_ASSESS_METHOD_START):
            continue

        # If the unfrozen module doesn't have a function that is found in the
        # original module, it's probably the case that the function was added
        # by us (e.g. a function added by some other policy node).
        if not hasattr(temp_module, name):
            continue

        try:
            source = inspect.getsource(getattr(temp_module, name))
        except Exception:
            logger.debug("No source found for function: %s", name)
            continue

        rewrite_and_patch_function(module, name, function, source)


def apply_rewrite_policy():
    if not Settings().is_rewriter_enabled:
        return

    for module in REWRITE_MODULES:
        rewrite_module_functions(module)


def reverse_rewrite_policy():
    for module in REWRITE_MODULES:
        reverse_module_patches_by_name(module)

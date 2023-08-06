# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Implements AST rewriter for Contrast Agent
"""
import importlib.abc
import importlib.machinery
import importlib.util
import types
import sys
import ast
import copy
import operator
import os
import re

# Seems like it is necessary to import this prior to rewriting to avoid some weird partial import state
import tokenize  # pylint: disable=unused-import

# NOTE: It is extremely important to limit the number of imports used by this
# module. It should be restricted to only those imports that are absolutely
# necessary for the operation of the rewriter, and ideally should include only
# built-in or standard library modules that are already imported by the
# interpreter prior to the evaluation of this module. It is *very* important
# that this module does *not* import the core `contrast` package since that
# would introduce a huge number of dependencies that we do not want.
# By limiting the number of dependencies for the rewriter module, we can ensure
# that a minimal number of modules are already imported prior to the
# application of the rewriter, which means we maximize the coverage of our
# rewriter in application and library code.

ENABLE_REWRITER: str = "__CONTRAST_APPLY_REWRITER"
REWRITE_FOR_PYTEST: str = "__CONTRAST_REWRITE_FOR_PYTEST"

_CONTRAST_MODULE_REGEX = re.compile(
    r"(contrast|contrast_vendor|contrast_rewriter)(\..+)?"
)
_CONTRAST_OPERATOR_NAME: str = "contrast__operator"
_REWRITER_ENABLED: bool = False

from contrast_vendor.wrapt.importer import _ImportHookChainedLoader


class DeferredLogger:
    def __init__(self):
        self.messages = []

    def debug(self, message, *args, **kwargs):
        self.messages.append(("debug", message, args, kwargs))


logger = DeferredLogger()


def _load_module(source, module: types.ModuleType, filename):
    """
    Convenience method to compile and execute the given module source

    It seems like we do not need any exception handling here since any
    exception that occurs gets handled further up by the import machinery and
    causes it to fall back on the original loader. This is definitely good for
    us since it means that even if we mess up here somehow, it shouldn't
    prevent the original module from being loaded. It will just be loaded
    without our rewrites.
    """
    code = compile(source, filename, "exec", dont_inherit=True)
    exec(code, module.__dict__)


def populate_operator_module(obj):
    obj.setdefault(_CONTRAST_OPERATOR_NAME, operator)


def _is_contrast_module_name(fullname: str) -> bool:
    return bool(_CONTRAST_MODULE_REGEX.fullmatch(fullname))


class ContrastMetaPathFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        """
        The finder is in charge of finding a module's "spec". The spec includes import
        machinery metadata about the module - including its name, source file path, and
        the loader, among others.

        Here, we first use importlib's default machinery to get the spec for the module
        about to be imported. The problem with this spec is that it also uses the
        default loader, which isn't what we want. To get around this, we reuse some
        metadata and generate a new spec that points at our loader.
        """
        if _is_contrast_module_name(fullname):
            return None

        spec = importlib.machinery.PathFinder.find_spec(fullname, path)

        if (
            spec is None
            or spec.origin is None
            or not isinstance(spec.loader, importlib.machinery.SourceFileLoader)
        ):
            logger.debug(
                "Skipping non-source module - fullname=%s, path=%s",
                fullname,
                getattr(spec, "origin", "<unknown>"),
            )
            return None

        new_spec = importlib.util.spec_from_file_location(
            fullname,
            spec.origin,
            loader=ContrastRewriteLoader(fullname, spec.origin),
            submodule_search_locations=spec.submodule_search_locations,
        )
        if new_spec is None:
            return new_spec

        loader = getattr(new_spec, "loader", None)

        if loader and not isinstance(loader, _ImportHookChainedLoader):
            new_spec.loader = _ImportHookChainedLoader(loader)

        logger.debug(
            "Updated spec for module: fullname=%s, path=%s",
            fullname,
            spec.origin,
        )
        return new_spec


class ContrastRewriteLoader(importlib.machinery.SourceFileLoader):
    def exec_module(self, module: types.ModuleType) -> None:
        """
        This method is responsible for actually doing the module `exec`-ing. We take
        control of this system and do the following:
        - read the original source file. We require pyc caching to be disabled for this
        - parse the source file into an AST
        - rewrite the AST
        - compile the AST into a code object
        - exec the code object

        Note that we add our custom add function to the module's globals. This prevents
        the need for import rewriting entirely
        """
        original_source_code = None
        filename = self.path

        # May be None in some cases such as for namespace packages
        if filename is None:
            return

        try:
            original_source_code = self.get_source(self.name)
            tree = ast.parse(original_source_code)
        except Exception as ex:
            logger.debug("WARNING: failed to rewrite %s", filename, exc_info=ex)

            _load_module(original_source_code, module, filename)

            return

        if _CONTRAST_OPERATOR_NAME not in module.__dict__:
            try:
                populate_operator_module(module.__dict__)
                PropagationRewriter().visit(tree)
                ast.fix_missing_locations(tree)
            except Exception as ex:
                logger.debug("WARNING: failed to rewrite %s", filename, exc_info=ex)
        else:
            logger.debug(
                "WARNING: module %s appears to have been already rewritten; will not rewrite again",
                filename,
            )

        _load_module(tree, module, filename)


class PropagationRewriter(ast.NodeTransformer):
    def _with_context(self, node, context):
        node = copy.copy(node)
        node.ctx = context
        return node

    def _make_attr(self, op):
        return ast.Attribute(
            value=ast.Name(id=_CONTRAST_OPERATOR_NAME, ctx=ast.Load()),
            attr=op.__name__,
            ctx=ast.Load(),
        )

    def visit_BinOp(self, binop: ast.BinOp):
        """
        If we see an "Add" or a "Mod" binary operation, replace it with a call to our custom add/modulo
        function, which includes all necessary instrumentation.
        """
        binop.left = self.visit(binop.left)
        binop.right = self.visit(binop.right)

        if isinstance(binop.op, ast.Mod):
            binop_replacement = ast.Call(
                func=self._make_attr(operator.mod),
                args=[binop.left, binop.right],
                keywords=[],
            )

            ast.copy_location(binop_replacement, binop)
            return binop_replacement

        if not isinstance(binop.op, ast.Add):
            return binop

        binop_replacement = ast.Call(
            func=self._make_attr(operator.add),
            args=[binop.left, binop.right],
            keywords=[],
        )
        ast.copy_location(binop_replacement, binop)
        return binop_replacement

    def visit_AugAssign(self, node: ast.AugAssign):
        """
        If we see an "Append", `+=` operation, rewrite it as a `+`.
        """
        node.value = self.visit(node.value)

        if not isinstance(node.op, ast.Add):
            return node

        target = left = None
        if isinstance(node.target, ast.Name):
            name = ast.Name(id=node.target.id)
            target = self._with_context(name, ast.Store())
            left = self._with_context(name, ast.Load())
        else:
            target = node.target
            left = self._with_context(target, ast.Load())

        call_contrast_append_node = ast.Assign(
            targets=[target],
            value=ast.Call(
                func=self._make_attr(operator.iadd),
                args=[self.visit(left), node.value],
                keywords=[],
            ),
        )

        ast.copy_location(call_contrast_append_node, node)
        # Recurse here in order to properly rewrite the `+` operation
        return call_contrast_append_node

    def visit_JoinedStr(self, node: ast.JoinedStr):
        return ast.Call(
            func=ast.Attribute(value=ast.Constant(""), attr="join", ctx=ast.Load()),
            args=[ast.List(elts=node.values, ctx=ast.Load())],
            keywords=[],
        )


def _non_contrast_module_filter(module_item) -> bool:
    return not _is_contrast_module_name(
        getattr(module_item[1], "__package__", "") or ""
    )


def _log_imported_modules() -> None:
    module_map = {
        importlib.machinery.BuiltinImporter: "builtin",
        importlib.machinery.FrozenImporter: "frozen",
    }

    all_modules = list(filter(_non_contrast_module_filter, sys.modules.items()))

    logger.debug("the following %d modules are already imported", len(all_modules))
    for name, module in sorted(all_modules):
        module_type = module_map.get(getattr(module, "__loader__", None), "source")
        logger.debug("%-20s type=%s", name, module_type)


def register(override_config=False):
    """
    Register our rewriter with the import system. After this call, any newly imported
    modules (from source code) will use our custom rewriter.

    Note that because this function is defined in the same module that defines our add
    replacement function, we never have to worry about rewriting the addition in the
    replacement function itself. If that were to occur, we would get an infinite
    recursion.

    Rewriter should only run in >=py3.10 and only in environments in which our default
    patching mechanism does not work.

    :param override_config: Force the rewriter to be registered regardless of configuration (for testing purposes)
    """
    global _REWRITER_ENABLED

    if not (override_config or os.environ.get(ENABLE_REWRITER)):
        logger.debug("Rewriter not enabled, exiting")
        return

    if is_rewriter_enabled():
        logger.debug("Rewriter already enabled, not applying again")
        return

    _log_imported_modules()

    sys.meta_path.insert(0, ContrastMetaPathFinder())

    logger.debug("enabled AST rewriter")

    _REWRITER_ENABLED = True


def deregister():
    """
    Remove our rewriter from the import system. Modules that were loaded by our rewriter
    will remain rewritten.

    Return True if we find and deregister our machinery, False otherwise.
    """
    global _REWRITER_ENABLED

    for i, finder in enumerate(sys.meta_path.copy()):
        if isinstance(finder, ContrastMetaPathFinder):
            sys.meta_path.pop(i)
            _REWRITER_ENABLED = False
            return True
    return False


def process_rewriter_logs(real_logger):
    for level, message, args, kwargs in logger.messages:
        getattr(real_logger, level)(message, *args, **kwargs)

    logger.messages.clear()


def is_rewriter_enabled() -> bool:
    return _REWRITER_ENABLED

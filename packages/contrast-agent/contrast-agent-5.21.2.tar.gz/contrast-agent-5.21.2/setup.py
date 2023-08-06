# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys
import platform
import tempfile
import time
from glob import glob
from io import open
from os import environ, path, system
from shutil import rmtree
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install_lib import install_lib

root_dir = path.abspath(path.dirname(__file__))


# This is where the version should be updated for releases
CONTRAST_RELEASE_VERSION = "5.21.2"

AGENT_LIB_REQUIREMENT = "~=0.5.4"


def read(*parts):
    with open(path.join(root_dir, *parts), encoding="utf-8") as f:
        return f.read()


def is_arm_mac():
    """
    determine if we're running on an ARM-based mac (M1, M2, etc)
    """
    return (
        "darwin" in platform.system().lower() and "arm" in platform.processor().lower()
    )


extension_path = path.join("contrast", "assess_extensions")
extension_source_dir = path.join("src", extension_path)
version_dir = path.join(extension_source_dir, "py{}{}".format(*sys.version_info[:2]))
common_dir = path.join(extension_source_dir, "common")

if sys.platform.startswith("darwin"):
    link_args = ["-rpath", "@loader_path"]
    platform_args = []
else:
    platform_args = ["-Wno-cast-function-type"]
    link_args = []

debug = environ.get("ASSESS_DEBUG")
debug_args = ["-g", "-O1"] if debug else []
macros = [("ASSESS_DEBUG", 1)] if debug else []
macros.append(("EXTENSION_BUILD_TIME", '"{}"'.format(time.ctime())))

strict_build_args = ["-Werror"] if environ.get("CONTRAST_STRICT_BUILD") else []

NO_FUNCHOOK = environ.get("CONTRAST_NO_FUNCHOOK")
if NO_FUNCHOOK:
    macros.append(("NO_FUNCHOOK", 1))
    c_sources = [
        path.join(common_dir, name)
        for name in [
            "patches.c",
            "scope.c",
            "logging.c",
            "intern.c",
            "propagate.c",
            "format.c",
            "repr.c",
            "repeat.c",
            "streams.c",
            "subscript.c",
            "cast.c",
            "trace.c",
        ]
    ]
    c_sources.extend(glob(path.join(extension_source_dir, "py3", "patches.c")))
    c_sources.extend(
        [
            path.join(version_dir, name + ".c")
            for name in ["iobase", "bytesio", "stringio"]
        ]
    )
    libraries = []
else:
    c_sources = glob(path.join(common_dir, "*.c")) + glob(path.join(version_dir, "*.c"))
    # Add source files common to all python3 versions
    c_sources.extend(glob(path.join(extension_source_dir, "py3", "*.c")))
    libraries = ["funchook"]


extensions = [
    Extension(
        "contrast.assess_extensions.cs_str",
        c_sources,
        libraries=libraries,
        include_dirs=[
            extension_source_dir,
            path.join(extension_source_dir, "include"),
        ],
        library_dirs=[extension_source_dir],
        # Path relative to the .so itself (works for gnu-ld)
        runtime_library_dirs=["$ORIGIN"],
        extra_compile_args=[
            "-Wall",
            "-Wextra",
            "-Wno-unused-parameter",
            "-Wmissing-field-initializers",
        ]
        + strict_build_args
        + debug_args
        + platform_args,
        extra_link_args=link_args,
        define_macros=macros,
    )
]

tempdir = None
funchook_temp = None

build_err_msg = "Failed to build Contrast C extension.\n"

arm_mac_err_msg = """
The Contrast Python Agent does not yet support the new ARM-based Macbooks (M1,
M2, etc). For an experimental, pre-beta build, try reinstalling the agent with
CONTRAST_NO_FUNCHOOK=1 set in your environment. Contrast will not provide
support for issues arising from the use of this build option.
"""

autotools_err_msg = """
It is necessary for autotools (autoconf, automake) to be installed in order for
Contrast to build properly. On lightweight systems such as Alpine, it may be
necessary to install linux-headers if they are not available already. Some
other systems may require "build essential" packages to be installed.
"""


class ContrastBuildExt(build_ext):
    def run(self):
        if NO_FUNCHOOK:
            build_ext.run(self)
            return

        if system("/bin/sh src/contrast/assess_extensions/build_funchook.sh") != 0:
            if not NO_FUNCHOOK and is_arm_mac():
                raise RuntimeError(
                    f"{build_err_msg}\n{arm_mac_err_msg}\n{autotools_err_msg}"
                )
            raise RuntimeError(f"{build_err_msg}\n{autotools_err_msg}")

        build_ext.run(self)

        global tempdir
        global funchook_temp

        ext = "dylib" if sys.platform.startswith("darwin") else "so"
        funchook_name = "libfunchook.{}".format(ext)
        funchook = path.join(extension_source_dir, funchook_name)

        tempdir = tempfile.mkdtemp("contrast-build")
        funchook_temp = path.join(tempdir, funchook_name)
        self.copy_file(funchook, funchook_temp)


class ContrastInstallLib(install_lib):
    def run(self):
        install_lib.run(self)

        if NO_FUNCHOOK:
            return

        if funchook_temp is not None:
            dest_dir = path.join(self.install_dir, extension_path)
            self.copy_file(funchook_temp, dest_dir)
            rmtree(tempdir)


if int(environ.get("CONTRAST_DEV_VERSION", "0")):
    version_config = dict(
        use_scm_version={
            # Parse out the issue name as prefix if it exists
            "tag_regex": (
                r"^(?P<prefix>(CONTRAST|PYT)-\d+/)?(?P<version>.*)(?P<suffix>)?"
            ),
            "git_describe_command": "git describe --tags --dirty --long",
        },
        setup_requires=["setuptools_scm"],
    )
else:
    version_config = dict(version=CONTRAST_RELEASE_VERSION)


setup(
    name="contrast-agent",
    description="Contrast Security's agent for Python web frameworks",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url="https://www.contrastsecurity.com",
    project_urls={
        "Change Log": "https://docs.contrastsecurity.com/en/python-agent-release-notes-and-archive.html",
        "Support": "https://support.contrastsecurity.com",
        "Trouble Shooting": "https://support.contrastsecurity.com/hc/en-us/search?utf8=%E2%9C%93&query=Python",
        "Wiki": "https://docs.contrastsecurity.com/",
    },
    # Author details
    author="Contrast Security, Inc.",
    author_email="python@contrastsecurity.com",
    # Choose your license
    license="CONTRAST SECURITY (see LICENSE.txt)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        # Audience
        "Intended Audience :: Developers",
        # License; commercial
        # supported languages
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="security development",
    # See MANIFEST.in for excluded packages
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"contrast": ["../data/policy.json"]},
    python_requires=">=3.7,<3.12",
    # NOTE: if install_requirements changes, update license_info.py accordingly
    install_requires=[
        "requests>=2.4.2,<3",
        f"contrast-agent-lib{AGENT_LIB_REQUIREMENT}",
    ],
    include_package_data=True,
    cmdclass=dict(build_ext=ContrastBuildExt, install_lib=ContrastInstallLib),
    ext_modules=extensions,
    extras_require={},
    entry_points={
        "console_scripts": [
            "contrast-python-run = contrast.scripts:runner",
            "contrast-fix-interpreter-permissions = contrast.scripts:fix_interpreter_permissions",
            "contrast-validate-config = contrast.scripts:validate_config",
            "contrast-propagator-check = contrast.scripts:propagator_check",
        ]
    },
    **version_config,
)

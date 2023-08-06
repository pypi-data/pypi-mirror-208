# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

import sys
import platform
import atexit
import threading

from typing import Optional

import contrast
from contrast import __version__, AGENT_CURR_WORKING_DIR
from contrast.utils.locale import DEFAULT_ENCODING
from contrast.agent import agent_lib, thread_watcher, patch_controller
from contrast.agent.assess.rules.providers.enable import enable_providers
from contrast.agent.settings import Settings
from contrast.reporting import ReportingClient, teamserver_messages
from contrast.reporting.reporting_client import MAX_ATTEMPTS
from contrast.assess_extensions import cs_str
from contrast.utils.loggers.logger import (
    setup_basic_agent_logger,
    setup_agent_logger,
    setup_security_logger,
)
from contrast.utils import timer
from contrast.utils.library_reader.library_reader import LibraryReader
from contrast.utils.namespace import Namespace
from contrast.utils.decorators import fail_loudly
from contrast_rewriter import process_rewriter_logs

# NOTE: policy is currently loaded/registered upon import
from contrast import policy  # pylint: disable=unused-import

logger = setup_basic_agent_logger()
LOGS_SEPARATOR = "-" * 120

if not contrast.telemetry_disabled():
    from contrast.agent.telemetry import Telemetry
else:
    Telemetry = None


def stop_telemetry(telemetry):
    if telemetry.message_q:
        if not telemetry.message_q.empty():
            telemetry.send_messages()

        assert telemetry.message_q.empty()


class module(Namespace):
    init_lock: threading.Lock = threading.Lock()
    is_initialized = False
    id: Optional[int] = None
    settings: Optional[Settings] = None
    reporting_client: Optional[ReportingClient] = None
    library_reader: Optional[LibraryReader] = None
    routes: dict = {}
    first_request: bool = True
    # NOTE: this field can be set prior to initialization
    framework: Optional[str] = None


def _log_environment():
    """
    Log current working directory, python version and pip version
    """
    banner = f"{'-' * 50}ENVIRONMENT{'-' * 50}"
    logger.debug(banner)
    logger.debug("Current Working Dir: %s", AGENT_CURR_WORKING_DIR)
    logger.debug("Python Version: %s", sys.version)
    logger.debug("Detected Framework: %s", module.settings.framework)
    logger.debug("Server Version: %s", module.settings.server)
    logger.debug("Contrast Python Agent Version: %s", __version__)
    logger.debug("Executable: %s", sys.executable)
    logger.debug("Default encoding %s", DEFAULT_ENCODING)

    try:
        platform_str = platform.platform()
    except Exception:
        try:
            platform_str = platform.platform(terse=True)
        except Exception:
            platform_str = "unknown"

    logger.debug("Platform %s", platform_str)

    try:
        import pip

        logger.debug("Pip Version: %s", pip.__version__)
    except Exception:
        logger.debug("Pip not found")

    logger.debug(banner)


def _warn_for_misleading_config():
    protect_enabled = module.settings.is_protect_enabled()
    assess_enabled = module.settings.is_assess_enabled()

    logger.info("Protect: %s", protect_enabled)
    logger.info("Assess: %s", assess_enabled)

    if protect_enabled and module.settings.config.get("assess.enable"):
        logger.warning("Protect is running but Assess is enabled in local config")
        logger.warning("Defaulting to Protect behavior only")

    if (
        module.settings.config.get("protect.enable")
        and not module.settings._is_defend_enabled_in_server_features()
    ):
        logger.warning("Protect enabled in local config but disabled by Teamserver")

    if (
        module.settings.is_agent_config_enabled()
        and not protect_enabled
        and not assess_enabled
    ):
        logger.warning("Neither Protect nor Assess is running")


def _successful_startup_msgs():
    if not _send_startup_msg_with_retries(teamserver_messages.ServerStartup()):
        return False
    if not _send_startup_msg_with_retries(teamserver_messages.ApplicationStartup()):
        return False
    return True


def _send_startup_msg_with_retries(msg):
    attempt = 1
    while True:
        if _send_startup_msg(msg):
            return True

        attempt += 1
        if attempt > MAX_ATTEMPTS:
            break

        logger.debug("%s: will retry - sleeping for 1 second", msg.class_name)
        timer.sleep(1)

    # TODO: PYT-2612 use the commented-out logic here instead
    # logger.error(
    #     "%s: Unexpected error from Contrast UI. Will not initialize Contrast Agent."
    # )
    # return False
    return True


def _send_startup_msg(msg):
    """
    Send a single startup message (ServerStartup or ApplicationStartup) immediately.
    This function runs in the main thread, and is blocking.

    Return False if the message needs to be retried, True otherwise.
    Note that we only need to retry if we get an ambiguous response (5xx).
    """
    response = module.reporting_client.send_message(msg)
    if response is None:
        return False
    msg.process_response(response, module.reporting_client)
    return response.status_code < 500


def initialize_libraries():
    """
    If enabled, read libraries from the application
    :return: True
    """
    if not module.settings.is_analyze_libs_enabled():
        return

    # Passing callback to send message due to a circular import issue, and a
    # deadlock occurring if something is imported inside of a function running in
    # this thread
    module.library_reader = LibraryReader(
        module.settings,
        send_ts_message_func=module.reporting_client.add_message,
    )
    module.library_reader.start_library_analysis_thread()


@fail_loudly("Unable to initialize Contrast Agent Settings.", return_value=False)
def initialize_settings():
    """
    Initialize agent settings.

    Returns True on settings being initialized and False if any failure.
    """
    module.settings = Settings(framework_name=module.framework)
    return True


def is_initialized() -> bool:
    return module.is_initialized


def get_settings():
    return module.settings


def get_reporting_client():
    return module.reporting_client


def get_routes():
    return module.routes


def update_routes(new_routes: dict):
    module.routes.update(new_routes)


def is_first_request():
    return module.first_request


def set_first_request(val: bool):
    module.first_request = val


@fail_loudly("Failed to register detected framework")
def set_detected_framework(name: str):
    """
    Registers the name of the detected framework

    It is safe to call this method prior to initialization of agent state. In
    order to be effective, this method should be called prior to middleware
    initialization.
    """
    module.framework = name


@fail_loudly("Failed to process logs from rewriter")
def _process_rewriter_logs(logger):
    logger.debug("Beginning deferred logs from rewriter")
    process_rewriter_logs(logger)
    logger.debug("Completed deferred logs from rewriter")


def initialize(name: Optional[str] = None):
    """
    If this method is called more than once per process, we use the is_initialized
    flag to only run the following work once:
        - library analysis thread initialization
        - turning on patches
        - hardcoded rule providers
        - scanning config rules
        - environment logging
        - loading common configuration
        - initializing settings

    In order to avoid a warning message, callers should check is_initialized()
    prior to calling this function.
    """
    with module.init_lock:
        if module.is_initialized:
            logger.warning("Attempted to initialize agent state more than once")
            return

        module.id = id(module)
        name = name or __name__

        logger.info('Initializing Contrast Agent "%s" [id=%s]', name, module.id)
        logger.info("Contrast Python Agent Version: %s\n", __version__)

        if not initialize_settings():
            return

        if module.settings is None or not module.settings.is_agent_config_enabled():
            logger.warning("Contrast Agent is not enabled.")
            return

        setup_agent_logger(module.settings.config)
        setup_security_logger(module.settings.config)
        module.settings.config.log_config()

        _log_environment()

        # The rewriter is applied long before we have any settings or logger so
        # the deferred logs are finally processed here
        _process_rewriter_logs(logger)

        cs_str.init_contrast_scope_cvars()

        module.reporting_client = ReportingClient()
        module.reporting_client.start()

        if not _successful_startup_msgs():
            logger.error("Unable to initialize Contrast Agent.", direct_to_teamserver=1)
            return

        _warn_for_misleading_config()

        # This MUST happen after the initialization calls for TeamServer messaging
        # (sending server start and application start) to ensure that TeamServer will
        # accept the messages sent by our background reporting threads
        # Skip telemetry since it is enabled later in this method
        thread_watcher.ensure_running(module, skip_telemetry=True)

        initialize_libraries()
        patch_controller.enable_patches()

        if module.settings.is_assess_enabled():
            # For now agent runtime starts before config scanning
            # this will be reset when time_limit_threshold is reached,
            # it doesn't symbolize the total agent runtime for all time.
            module.settings.agent_runtime_window = timer.now_ms()

            enable_providers()
            # NOTE: This should stay in middleware
            # scan_configs_in_thread()

        if module.settings.is_protect_enabled() and not agent_lib.initialize():
            logger.error("Fatal: Unable to initialize agent-lib. Disabling Contrast.")
            module.settings.config.put("enable", False)
            return

        logger.info(
            "Finished Initializing Contrast Agent %s [id=%s] \n\n%s\n",
            name,
            module.id,
            LOGS_SEPARATOR,
        )

        if Telemetry is not None:
            contrast.TELEMETRY = Telemetry()
            contrast.TELEMETRY.start()
            atexit.register(stop_telemetry, contrast.TELEMETRY)

        module.is_initialized = True

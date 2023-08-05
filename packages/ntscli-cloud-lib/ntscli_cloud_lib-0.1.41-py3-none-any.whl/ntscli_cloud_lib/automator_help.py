#  Copyright (c) 2020 Netflix.
#  All rights reserved.
#
import sys
from logging import getLogger
from typing import Callable

logger = getLogger("ntscli-cloud-lib")

NO_DEVICE_ID = "No device locator was provided"
BAD_DEVICE_ID = "Failed to lookup device"
CANCEL_OR_TRY_LATER = "Device is currently busy"
DEVICE_NEVER_STARTED = "INT did not receive any events from the device"
DEVICE_STOPPED_AFTER_STARTING = "INT has not received any events from the device in over"
REQUEST_STATUS_FAILED = "automator request failed without talking to the automator."
INCOMPLETE_PLAN_REQUEST_ERROR = "body missing"
MISSING_RAE_TARGET = "rae id missing"
CLOUD_TARGET_MISSING = "The SSL configuration for the named broker is missing"
CLOUD_TARGET_INCOMPLETE = "The SSL configuration for the named broker is incomplete"


def log_and_print(message: str):
    logger.error(message)
    print(message)


user_guidance_map = {
    NO_DEVICE_ID: "\tIt looks like you didn't provide a device identifier in your request to the automator. Make sure you "
    'provide something like this: "target": {"esn":"foo", "rae": "r3000111"}',
    BAD_DEVICE_ID: "\tThe device ID you provided is missing from Network Agent and/or the ADB module. Open the RAE web UI and "
    "validate it responds to start and stop commands, copy-paste the ESN back to your command, and if that "
    "doesn't work, restart all the automator related modules.",
    CANCEL_OR_TRY_LATER: "\tThe automator thinks the device is busy. You can issue a cancel to stop what it is doing and then "
    "issue a new request.",
    DEVICE_NEVER_STARTED: "\tThe automator told the device to start, but the device never started sending messages to the "
    "automator. DIAL or ADB may need assistance to get the device to a known good state, such as "
    "trusting ADB or using DIAL stop and start commands to get the device into a state known to DIAL.",
    DEVICE_STOPPED_AFTER_STARTING: "\tThe device started running tests, but stopped responding before the test ended. This "
    "usually means a test crashed outright.",
    REQUEST_STATUS_FAILED: "\tThe request to the automator failed without actually reaching the automator. This could mean "
    "the mqtt-router service is not responding, or that the automator is not installed, or not responding. Open the RAE web UI on the "
    "target RAE and make sure the Automator module is installed and running.",
    INCOMPLETE_PLAN_REQUEST_ERROR: '\tThe test plan response came back without response["body"]["error"]: File a ticket and we can help '
    "diagnose this and provide hints.",
    MISSING_RAE_TARGET: "\tThe RAE ID was missing or invalid. We accept the rae serial number form: r3000111",
    "Connection refused": "\tThe remote AWS IoT broker actively refused requests to connect. This could mean an incorrect security "
    "configuration, or networking problems.",
    CLOUD_TARGET_MISSING: "\tThe configuration directory for the destination MQTT broker (defaults to 'cloud') is missing. Look for the directory in ~/.config/netflix",
    CLOUD_TARGET_INCOMPLETE: "\tThe configuration directory for the destination MQTT broker (defaults to 'cloud') is incomplete. The best option to repair this is to delete the configuration from ~/.config/netflix, and then download a fresh copy from the Netflix partner portal and put it in ~/.config/netflix",
}


def guide_user(error_string: str) -> None:
    """
    Provide user guidance for errors from the automator.

    Always raises ValueError, but with a user prompt.
    Patterns and user prompts are stored above.

    :param error_string: A string to print help for, and then raise ValueError
    :return:
    """
    log_and_print("")

    for pattern in user_guidance_map.keys():
        if pattern in error_string:
            log_and_print(
                f"""\tReceived this error:
==========
{error_string}
==========


{user_guidance_map[pattern]}
==========
"""
            )
            return

    log_and_print(
        f"""\tReceived this error:
==========
{error_string}
==========
"""
    )


def user_guidance_decorator(func: Callable):
    """
    Handle uncaught errors by printing helpful messages.
    """

    def print_help_and_exit(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except BaseException as ee:
            guide_user(str(ee))

    return print_help_and_exit


def hide_stacktraces_decorator(func: Callable):
    """
    Handle uncaught errors by forcefully exiting the process.

    This is meant to be the last line of defense against uncaught errors.
    """

    def just_exit(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except BaseException:
            sys.exit(-1)

    return just_exit

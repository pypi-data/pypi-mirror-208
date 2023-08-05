#  Copyright (c) 2020 Netflix.
#  All rights reserved.
import re

from ntscli_cloud_lib.automator import DeviceIdentifierTarget as AutomatorIdentifier
from ntscli_cloud_lib.log import logger


def is_rae_name_pattern(userstring):
    pattern = r"^r\d{7}$"
    foundparts = re.findall(pattern, userstring)
    if len(foundparts) == 1:
        return True
    else:
        return False


def sanity_check(id_to_check: AutomatorIdentifier) -> bool:
    """
    Perform a basic sanity check on a dict to see if it contains an identifier.

    Note that the value of the identifier is not checked, even for formatting.

    :param id_to_check:
    :return:
    """
    valid = id_to_check.target is not None and (
        id_to_check.target.ip is not None
        or id_to_check.target.esn is not None
        or id_to_check.target.serial is not None
        or id_to_check.target.rae is not None
    )
    if valid:
        valid = id_to_check.target.rae is None or is_rae_name_pattern(id_to_check.target.rae)

    if not valid:
        logger.error("The device identifier is missing some values to make it valid.")
        logger.error(
            "A device identifier is a JSON object stored at the key 'target', with one or more of the keys 'esn', 'ip', 'rae', "
            "and 'serial': "
        )
        logger.error('{"target": {"esn": "NFANDROID...", "ip": "192...", "rae": "r3000100"}, ...')

        logger.error(
            "The rae can be looked up if the ESN is provided. The device registry will try to resolve other combinations if it can."
        )

    return valid

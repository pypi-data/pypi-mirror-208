"""Main module."""
import re

from .__version__ import __version__

__all__ = [__version__]

from .log import logger


def host_to_rae_name(userstring: str) -> str:
    """
    Return a RAE serial string from most things a user types

    :param userstring: The RAE host/ip or connection configuration to connect to.
    :return: None
    """
    pattern = r"r\d+"
    foundparts = re.findall(pattern, userstring)
    if len(foundparts) > 0:
        if len(foundparts[0]) != 8:
            logger.error(f"We could not parse a valid RAE number, such as r3456789 from your RAE string: {userstring}")
            return ""
        return foundparts[0]
    return ""


def click_sanitize_rae_names(ctx, param, value):
    """
    Sanitize --rae parameters if using the click library.

    To use this, provide this as a callback to a click option or argument:
    @click.option("--rae", callback=click_sanitize_rae_names)

    :param ctx:
    :param param:
    :param value:
    :return:
    """
    if value is not None:
        if isinstance(value, str):
            to_return = host_to_rae_name(value)
            if to_return == "":
                raise SystemExit("The RAE name did not parse. Valid example: r3000100")
            return to_return
        if isinstance(value, tuple):
            to_return = tuple(host_to_rae_name(x) for x in value)
            for x in to_return:
                if x == "":
                    raise SystemExit("The RAE name did not parse. Valid example: r3000100")
            return to_return

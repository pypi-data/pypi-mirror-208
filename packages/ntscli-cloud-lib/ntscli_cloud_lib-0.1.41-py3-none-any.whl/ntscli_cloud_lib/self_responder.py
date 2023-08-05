#  Copyright (c) 2020 Netflix.
#  All rights reserved.
import json
import uuid
from threading import Event

from kaiju_mqtt_py import KaijuMqtt
from kaiju_mqtt_py import MqttPacket

from ntscli_cloud_lib.log import logger
from ntscli_cloud_lib.session import IOT_BASE_PATTERN
from ntscli_cloud_lib.session import SSL_CONFIG_INCOMPLETE
from ntscli_cloud_lib.session import SSL_CONFIG_MISSING
from ntscli_cloud_lib.sslconfig import SslConfig
from ntscli_cloud_lib.sslconfigmanager import SslConfigManager

PING_REQUEST = {"status": 200, "self_test": True}


def responder(topic: str, msg: MqttPacket, *args, **kwargs):
    """Respond to self-ping formatted messages by returning an object."""
    logger.debug("User responder called")
    response = True
    if {"request": "something"} != msg.payload:
        response = False
    return {"status": 200, "body": {"response": response}}


class SelfResponder:
    """
    Connection checking through pub/sub.

    Can I subscribe and publish messages on a remote cloud broker, with no external services?
    """

    def __init__(self):
        """Constructor."""
        self.happened = Event()
        self.kaiju = KaijuMqtt()
        self.topic = ""

    def start(self, broker):
        """Start a unique handler for this client connection."""
        logger.debug(f"SelfResponder connecting to broker {broker}")

        manager = SslConfigManager()
        logger.debug(f"Looking for configuration {broker}")
        if not manager.has(broker):
            logger.debug(f"Could not find configuration {broker}, raising ValueError.")
            raise ValueError(SSL_CONFIG_MISSING)
        config: SslConfig = manager.get(broker)
        if not config.iscomplete():
            logger.debug(f"Configuration {broker} incomplete, raising ValueError.")
            raise ValueError(SSL_CONFIG_INCOMPLETE)
        context = config.get_ssl_context()
        self.kaiju.set_ssl_context(ssl_context=context, certificate_id_for_topics=config.certificate_id_topic_string)
        try:
            self.kaiju.connect(config.host, config.port)
            self.topic = IOT_BASE_PATTERN.format(self.kaiju.certificate_id) + "/client_self_responder/" + str(uuid.uuid4())
            logger.debug(f"SelfResponder registering to handle topic: {self.topic}")
            self.kaiju.handle(self.topic, responder)
        except Exception as ee:
            if "Connect timed out" in str(ee):
                logger.critical("The remote broker did not accept the connection after 15 seconds.")
                logger.critical("This could indicate a service outage, network routing or firewall issues, or other problems.")
                raise ConnectionError("The remote broker did not finish accepting the connection after 15 seconds.")
            raise ee

    def check_request(self):
        """
        Send a request to the remote broker, and check that we sent it.

        If the response is not sent back to us, we will typically get a timeout message,
        which will fail these assert checks.
        """
        logger.debug("SelfResponder requesting a response")
        response = self.kaiju.request(self.topic, {"request": "something"})
        logger.debug(f"SelfResponder response: {response}")
        try:
            if 500 == response["status"] and "Timed out." == response["body"]["error"]:
                logger.error("The connection to the remote broker timed out.")
                logger.error("If you were already connected, this might be a temporary network or service outage.")
                logger.error("If you have not been connected yet, you may have ssl configuration directory problems.")
                raise ValueError("The connection to the remote broker timed out.")
        except KeyError:
            # it wasn't our template timed-out error, proceed with other error checks. This is the ideal path.
            pass

        try:
            if 200 != response["status"]:
                raise ValueError(f"The response did not time out, but did return an error: {json.dumps(response)}")
        except KeyError:
            pass

    def stop(self):
        """Tear down our handler."""
        self.kaiju.close()

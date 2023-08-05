#  Copyright (c) 2020 Netflix.
#  All rights reserved.
import base64
import json
import random
import string
import zlib
from threading import Lock
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

import arrow
from betterproto import Casing
from kaiju_mqtt_py import KaijuMqtt

from ntscli_cloud_lib.automator import AvafPeripheralListRequest
from ntscli_cloud_lib.automator import DeviceIdentifier
from ntscli_cloud_lib.automator import DeviceIdentifierTarget
from ntscli_cloud_lib.automator import GetTestPlanRequest
from ntscli_cloud_lib.automator import GetTestPlanRequestOptions
from ntscli_cloud_lib.automator import HttpLikeAvafPeripheralListResponse
from ntscli_cloud_lib.automator import HttpLikeCancelResponse
from ntscli_cloud_lib.automator import HttpLikeErrorResponse
from ntscli_cloud_lib.automator import HttpLikeGetTestPlanResponse
from ntscli_cloud_lib.automator import HttpLikeStatusResponse
from ntscli_cloud_lib.automator import HttpLikeTestPlanRunResponse
from ntscli_cloud_lib.automator import StatusRequest
from ntscli_cloud_lib.automator import TestPlanRunRequest
from ntscli_cloud_lib.log import logger
from ntscli_cloud_lib.mqtt_retryable_error import MqttRetryableError
from ntscli_cloud_lib.sslconfig import SslConfig
from ntscli_cloud_lib.sslconfigmanager import SslConfigManager

CLOUD_BROKER: str = "cloud"
NTSCLI: str = "ntscli"
RESPONSE: str = "response"
BUSY_DEVICE: str = (
    "\nThe automator reports that the device is busy and could not accept your request. You may "
    "choose to wait, or cancel the current test plan before this request can succeed."
)
MISSING_DEVICE: str = (
    "\nThe device was not found in the device list. "
    "You were looking for:\n{}\n"
    "See if you can start and stop Netflix on your device from the Network Agent UI on the RAE."
)
BROKER_UP_REQUEST_TIMEOUT: str = "The broker is responding, but the request failed without talking to the RAE."
BROKER_UP_REQUEST_TIMEOUT_ON_RAE: str = "The broker is responding, but the request failed without talking to the modules on RAE {}"
RUN_REJECTED: str = "The automator rejected the request to run tests"
DEVICE_NOT_RECOGNIZED: str = "The RAE does not recognize the device identifier:\n{}"
IOT_BASE_PATTERN: str = "client/partner/{}"
TOPIC_REQUIRES_CONNECTION: str = (
    "The connection has not been made yet, so we can't form the topic string. Please call connect() before issuing other calls."
)
SSL_CONFIG_MISSING: str = (
    "The SSL configuration for the named broker is missing. Check the ~/.config/netflix/ directory for configuration directories."
)
SSL_CONFIG_INCOMPLETE: str = (
    "\nThe SSL configuration for the named broker is incomplete. Check the ~/.config/netflix/ directory for configuration directories.\n"
    "Each subdirectory should include .crt, .pem, and other files to create the connection with. Contact Netflix to create one of these "
    "configurations for you."
)
QOS: str = "qos"
TIMEOUT: str = "timeoutMs"
TARGET: str = "target"
BROKER_KEY: str = "broker"
CERTIFICATE_ID: str = "certificate_id"
PERIPHERAL_LIST_MISSING = "The peripheral list API did not include a list of peripherals."
DEFLATE_BYTE_LIMIT: int = 120 * 1024  # originally these were set differently, but it's nice to have them separate even now
MAX_MESSAGE_BYTE_LIMIT: int = 120 * 1024


class AutomatorStrings:
    """Strings sent from the Automator, in case they change."""

    MISSING_DEVICE: str = "Failed to lookup"
    BUSY_DEVICE: str = "Device is currently busy"
    NOT_RUNNING_TESTS: str = "Target device is not running tests"
    CANCEL_REQUEST_ACCEPTED: str = "Request to cancel running test accepted"


def make_explicit_batch_id() -> str:
    """
    Make a string to use as a shared batch ID across multiple runs.

    ntscli-${utils.randomString(8)} -${new Date().toISOString()}
    Example from something on my screen:
    "lastBatch":"ntscli-GT5FDI3F-2020-04-20T16:07:21.063Z"
    """
    randstr = ("".join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])).upper()  # nosec B311  not used for crypto
    datestr = arrow.utcnow().isoformat().replace("+00:00", "Z")
    return f"ntscli-{randstr}-{datestr}"


def optionally_compressed_dict(source_dict: dict) -> dict:
    """Get the json representation of a payload, compressing if required."""
    serialized: str = json.dumps(source_dict)
    serialized_length: int = len(serialized)
    logger.info(f"Preparing to publish payload {serialized}")

    if serialized_length < DEFLATE_BYTE_LIMIT:
        return source_dict

    # self.logger.info(f"Compressing {serialized_length} byte payload")
    deflate_bytes: bytes = zlib.compress(serialized.encode("utf-8"))
    encoded_string: str = base64.b64encode(deflate_bytes).decode("utf-8")
    replacement_dict: dict = {"deflated": encoded_string}
    if "target" in source_dict:
        replacement_dict["target"] = source_dict["target"]
    serialized = json.dumps(replacement_dict)
    serialized_length = len(serialized)

    if serialized_length > MAX_MESSAGE_BYTE_LIMIT:
        msg = f"The compressed message was still over the maximum byte limit. byte size {serialized_length}"
        logger.error(msg)
        raise ValueError(msg)

    return replacement_dict


def optionally_expanded_dict(source_dict: dict) -> dict:
    """If we get a deflated dict, expand it to the expected format."""


def is_valid_uuid(uuid_to_test: str):
    try:
        UUID(uuid_to_test, version=4)
        return True
    except ValueError:
        return False


class Session:
    """
    A stateful connection to the AWS IoT broker for communicating with mqtt-router.

    This object only tracks state surrounding the KaijuMqtt connection.
    """

    def __init__(self):
        """Constructor."""
        self.broker: str = CLOUD_BROKER
        self.kaiju: KaijuMqtt = KaijuMqtt()
        self.cleanup_funcs: List = []
        self.cloud_topic_format: bool = False
        # this is the intended rae target in the format r3000123 so we can for topics with it
        self.rae_topic_string: Optional[str] = None
        self.connection_lock: Lock = Lock()

    def _topic_with_session_id(self, command: str) -> str:
        """
        Form a topic with the session ID embedded.

        This is only possible after the ssl configuration has been loaded, which is typically during
        the connect() call.

        :param command: The test_runner subcommand to add
        :return:
        """
        # also provide command
        if self.kaiju.certificate_id == "":
            raise ValueError(TOPIC_REQUIRES_CONNECTION)
        return (IOT_BASE_PATTERN + "/test_runner/{}").format(self.kaiju.certificate_id, command)

    def connect(self, broker: str = "cloud") -> None:
        """
        Connect the underlying broker.

        The client should explicitly call mysession.destructor() to clean up.

        If the configuration for the broker configuration named is missing or incorrect, an error will be thrown.

        :return: None
        """
        self.broker = broker
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
        with self.connection_lock:
            try:
                self.kaiju.connect(config.host, config.port)
            except Exception as ee:
                if "Connect timed out" in str(ee):
                    logger.critical("The remote broker did not accept the connection after 15 seconds.")
                    logger.critical("This could indicate a service outage, network routing or firewall issues, or other problems.")
                    raise ValueError("The remote broker did not finish accepting the connection after 15 seconds.")

    def subscribe(self, topic: str, newfunc: Callable, options_dict: Dict = None) -> None:
        """
        Subscribe to a topic on the MQTT broker.

        This typically would be used to subscribe to the status stream of a test plan.

        The signature of the new function should be:
        def handle_updates(client, userdata, packet):
            ...

        This is the normal shape for a paho-mqtt topic message subscriber. The most interesting arg is packet.payload,
        of type dict.

        :param topic:
        :param newfunc:
        :param options_dict:
        :return:
        """
        options = options_dict if options_dict else {QOS: 1, TIMEOUT: 15000}
        cleanup = self.kaiju.subscribe(topic, newfunc, options)

        self.cleanup_funcs.append(cleanup)

    def get_test_plan_for_device(
        self, device: DeviceIdentifier, options: Optional[GetTestPlanRequestOptions] = None, type: Optional[str] = None
    ) -> HttpLikeGetTestPlanResponse:
        """
        Request a test plan from the remote Automator.

        :param device: The DeviceIdentifier to use in the data section of the request.
        :return: The response from the Automator module as a dict.
        """
        topic = self._topic_with_session_id("get_testplan")
        # using camel casing b/c options.testcaseId should stay that instead of testcase_id
        request = GetTestPlanRequest(target=device, type=type)
        if options:
            if options.test_plan_type == "playlist":
                if not is_valid_uuid(options.playlist_id):
                    raise ValueError(
                        "The playlist ID should be a UUID 4 string copied from NTS at 'https://partnertools.nrd.netflix.com/nts/#playlist'."
                        f"Because {options.playlist_id} was not a valid UUID, we will stop here."
                    )
                else:
                    request.options = options
            else:
                request.options = options

        dict_response = self._request(
            topic,
            request.to_dict(casing=Casing.CAMEL),
            options={QOS: 1, TIMEOUT: 5 * 60 * 1000},
        )
        self._raise_on_disconnect_or_error(dict_response, device, "getting a test plan")

        response = HttpLikeGetTestPlanResponse().from_dict(value=dict_response)
        if len(response.body.testcases) < 1:
            raise ValueError("The returned test case list was empty.  Can this device run tests currently in NTS-web?")

        return response

    def _check_broker(self):
        """
        Use a self-responder to check whether the broker is responding.

        This is used if a call fails and we want to make sure the broker is responding, even if the remote service is
        not.

        It does create a new, separate Session/connection during the check.
        """
        from ntscli_cloud_lib.self_responder import SelfResponder

        responder = SelfResponder()
        try:
            responder.start(self.broker)
            responder.check_request()
        except ValueError:
            raise ConnectionError("Unable to send and receive messages to remote broker")
        finally:
            responder.stop()

    def run_plan(self, request: TestPlanRunRequest) -> HttpLikeTestPlanRunResponse:
        """
        Send a request to run a specified test plan.

        Be sure to note the batch ID reported at log level WARNING or in the response JSON if you want to find the batch without visiting
        the web UI.

        :param request: The request to send, including the test plan.
        :return: The response from the Automator module as a dict.
        """
        topic = self._topic_with_session_id("run_tests")
        logger.debug(f"Preparing to post to topic: {topic}")

        # PDI-531: use snake case to send things to Automator, per verbal
        dict_response: Dict = self._request(topic, request.to_dict(casing=Casing.SNAKE), {QOS: 1, TIMEOUT: 60 * 1000})

        self._raise_on_disconnect_or_error(dict_response, request.target, "running a test plan")

        response = HttpLikeTestPlanRunResponse().from_dict(value=dict_response)
        if response.body.message and "Executing testplan on target." not in response.body.message:
            if AutomatorStrings.BUSY_DEVICE in response.body.message:
                # busy message looks similar to this:
                # {'status': 200,
                # 'body': {'status': 'running', 'message':
                #          'Device is currently busy running tests, request test cancellation or try again later'}}
                logger.info(BUSY_DEVICE)
                raise MqttRetryableError(BUSY_DEVICE)

            elif AutomatorStrings.MISSING_DEVICE in response.body.message:
                """The not-found-device message looks like this:
                {'status': 200, 'body':
                {'message': 'Failed to lookup device based on the data provided, please double check data,
                launch Netflix and try again', 'error': 'Error: Failed to lookup device based on the data provided,
                please double check data, launch Netflix and try again ... (stack trace)'}}
                """
                raise ValueError("The RAE could not locate the device identifier")

            raise ValueError("{}:\n{}".format(RUN_REJECTED, response.body.message))

        if response.body.batch_id is not None:
            logger.warning(f"Scheduled batch ID {response.body.batch_id}")

        return response

    def _raise_on_disconnect_or_error(self, dict_response: Dict, target: DeviceIdentifier, action_description: str):
        # Re-shape the source dict to be consistent with more errors
        if "body" in dict_response and "status" in dict_response["body"] and dict_response["body"]["status"] == "error":
            logger.error("Detected an error in most recent response")
            if "message" in dict_response["body"] and "error" not in dict_response["body"]:
                # move the message to where errors are expected and then process
                logger.error("Copying error message to the error field")
                dict_response["body"]["error"] = dict_response["body"]["message"]
                dict_response["body"]["status"] = 500
                del dict_response["body"]["message"]

        error = HttpLikeErrorResponse().from_dict(value=dict_response)
        if error.status == 401:
            # 401 means the RAE was not found typically
            logger.error(json.dumps(dict_response))
            raise ValueError(f"The RAE in the request was not found: {error.body.error}")
        elif error.status != 200:
            # status 500 is a timeout
            # this could mean we are having broker issues -- check it ourselves
            self._check_broker()
            # if you get past _check_broker, the broker works, now it's one circle farther away
            logger.error(json.dumps(dict_response))
            if target.rae:
                raise ConnectionError(BROKER_UP_REQUEST_TIMEOUT_ON_RAE.format(target.rae))
            raise ConnectionError(BROKER_UP_REQUEST_TIMEOUT)
        if error.body.error is not None:
            # explicit error from the automator
            logger.error(json.dumps(dict_response))
            if AutomatorStrings.MISSING_DEVICE in error.body.error:
                raise MqttRetryableError(MISSING_DEVICE.format(target.to_json()))
            else:
                raise ValueError(f"Error included in response while {action_description}\n{error.body.error}")
        if error.body.message is not None:
            if AutomatorStrings.NOT_RUNNING_TESTS in error.body.message or AutomatorStrings.CANCEL_REQUEST_ACCEPTED in error.body.message:
                return  # this is not an error

            logger.info(json.dumps(dict_response))
            if AutomatorStrings.BUSY_DEVICE in error.body.message:
                # busy message looks similar to this:
                # {'status': 200,
                # 'body': {'status': 'running', 'message':
                #          'Device is currently busy running tests, request test cancellation or try again later'}}
                logger.info(BUSY_DEVICE)
                raise MqttRetryableError(BUSY_DEVICE)
            elif AutomatorStrings.MISSING_DEVICE in error.body.message:
                raise MqttRetryableError(MISSING_DEVICE.format(target.to_json()))

    def cancel_plan_for_device(self, device: DeviceIdentifier) -> HttpLikeCancelResponse:
        """
        Request that we cancel the tests for this device.

        :param device: Which device to cancel for.
        :return: dict with keys status and body. Status will be a typical HTTP error code.
        """
        topic = self._topic_with_session_id("cancel_tests")
        dict_response = self._request(topic, DeviceIdentifierTarget(target=device).to_dict())
        response = HttpLikeCancelResponse().from_dict(value=dict_response)
        action_description = "cancelling tests"
        try:
            self._raise_on_disconnect_or_error(dict_response, device, action_description)
        except ConnectionError:
            # this is actually ok because the cancel will return non-200 sometimes
            pass
        return response

    def destructor(self):
        """
        Cleanly shut down the KaijuMqtt object and disconnect.

        Some unsubscribe actions need to be performed on shutdown of the client. I'd suggest putting this in a finally:
        clause to prevent strange behaviors. It is safe to call this multiple times.

        :return:
        """
        [x() for x in self.cleanup_funcs]
        with self.connection_lock:
            self.kaiju.close()

    def get_eyepatch_connected_esn_list(self, rae: str) -> List[str]:
        """
        Get the list of devices for which an EyePatch is connected.

        from v1.1
        Abstracted due to the intent to change the implementation later.

        :param rae: The RAE to request the list of connected devices from. Requires the EyePatch module to be installed.
        :return: list of strings, which are the ESNs with detected eyepatch configurations.
        """
        avaf_peripheral_list_topic = IOT_BASE_PATTERN.format(self.kaiju.certificate_id) + "/avaf/execute/peripheral.list"
        device = DeviceIdentifier(rae=rae)
        req = AvafPeripheralListRequest(type="eyepatch", target=device)
        dict_response: Dict = self._request(avaf_peripheral_list_topic, req.to_dict())

        self._raise_on_disconnect_or_error(dict_response, device, "getting eyepatch device list")

        try:
            reply: HttpLikeAvafPeripheralListResponse = HttpLikeAvafPeripheralListResponse().from_dict(dict_response)
        except KeyError:
            toreport = ValueError("There was no body in the response to the peripheral list request.")
            raise toreport

        if len(reply.body) < 1:
            logger.debug(PERIPHERAL_LIST_MISSING)
            logger.debug(dict_response["body"])
            return []
        returnme: List[str] = [peripheral.esn for peripheral in reply.body if peripheral.esn != ""]
        return returnme

    def is_esn_connected_to_eyepatch(self, rae: str, esn: str) -> bool:
        """
        Convenience call to find out an ESN has an EyePatch.

        from v1.1.

        :param esn: The ESN of the device we are interested in. Note that this is not using the DeviceIdentifier.
        :param rae: The RAE to request the list of connected devices from. Requires the EyePatch module to be installed.
        :return:
        """
        return esn in self.get_eyepatch_connected_esn_list(rae)

    def status(self, rae: str, **kwargs) -> Tuple[HttpLikeStatusResponse, Dict]:
        """Get status."""
        device: DeviceIdentifier = kwargs.get("device", None)
        topic = self._topic_with_session_id("status")
        request = StatusRequest(target=device, batch_id=(kwargs.get("batch_id", None)))
        if request.target is None:
            request.target = DeviceIdentifier()
        if request.target.rae is None:
            request.target.rae = rae

        dict_response = self._request(topic, request.to_dict(casing=Casing.SNAKE), {QOS: 1, TIMEOUT: 15000})
        self._raise_on_disconnect_or_error(dict_response, device, "getting status")
        return HttpLikeStatusResponse().from_dict(value=dict_response), dict_response

    def get_result_for_batch_id(self, device: DeviceIdentifier, batch_id: str) -> Tuple[HttpLikeStatusResponse, Dict]:
        """
        Get the result block for a specified batch ID.

        This is a convenience method over the status method to get the result of a batch ID on a device.
        """
        return self.status(device=device, rae=device.rae, batch_id=batch_id)

    def get_device_list(self, rae: str) -> List[DeviceIdentifier]:
        """
        Get the list of known devices behind the Automator.

        :return:
        """
        request = DeviceIdentifierTarget(target=DeviceIdentifier(rae=rae))
        topic = self._topic_with_session_id("list_targets")
        resp = self._request(topic, request.to_dict(), {QOS: 1, TIMEOUT: 15000})
        self._raise_on_disconnect_or_error(resp, request.target, f"getting the list of devices behind {rae}")
        return [DeviceIdentifier(**elt, rae=rae) for elt in resp["body"]]

    def _request(self, topic: str, source_dict: dict, options: Optional[dict] = None) -> dict:
        """
        Deflate and inflate payloads during requests.

        from v2.0
        """
        response: dict = self.kaiju.request(topic, optionally_compressed_dict(source_dict), options)
        try:
            if "body" in response and "deflated" in response["body"]:
                logger.info(f"Received compressed response: {response['body']['deflated']}")
                decoded_bytes = base64.b64decode(response["body"]["deflated"])
                json_string_bytes = zlib.decompress(decoded_bytes)
                # just swap out the compressed bytes
                del response["body"]["deflated"]
                response.update({"body": json.loads(json_string_bytes.decode("utf-8"))})
        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            # implicit catch if body key is missing, as well as normal JSON decode issues
            logger.info(f"failed to parse key 'body' in payload as JSON: {response}")
            response = {"status": 500, "error": "failed to parse key 'body' in payload as JSON", "msg": response["body"]["deflated"]}
        except zlib.error:
            logger.info(f"A compressed payload was present, but did not decompress correctly. {response}")
            response = {
                "status": 500,
                "error": f"A compressed payload was present, but did not decompress correctly. Contact Netflix for help. {response['body']['deflated']}",
                "msg": response["body"]["deflated"],
            }
        return response

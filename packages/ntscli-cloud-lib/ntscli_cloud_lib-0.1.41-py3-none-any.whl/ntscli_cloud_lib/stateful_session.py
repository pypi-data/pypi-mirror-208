#  Copyright (c) 2020 Netflix.
#  All rights reserved.
import copy
import ssl
from contextlib import contextmanager
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple

from betterproto import Casing

from ntscli_cloud_lib.automator import DeviceIdentifier
from ntscli_cloud_lib.automator import DeviceIdentifierTarget
from ntscli_cloud_lib.automator import GetTestPlanRequestOptions
from ntscli_cloud_lib.automator import HttpLikeCancelResponse
from ntscli_cloud_lib.automator import HttpLikeStatusResponse
from ntscli_cloud_lib.automator import TestPlanRunRequest
from ntscli_cloud_lib.automator_help import INCOMPLETE_PLAN_REQUEST_ERROR
from ntscli_cloud_lib.automator_help import REQUEST_STATUS_FAILED
from ntscli_cloud_lib.log import logger
from ntscli_cloud_lib.session import Session


class StatefulSession:
    """
    A simplified client for testing a single device at a time.

    This object handles state of the connection to the cloud agent, a single device, and a single test plan.

    This object also simplifies getting status updates. Any object that implements StatusWatcherInterface
    can be appended to this.status_watchers to get updates as the run progresses.
    """

    def __init__(self, **kwargs):
        """
        Construct a new StatefulSession. kwargs are passed to the DeviceIdentifier constructor.

        :param kwargs: Passed unmodified to the DeviceIdentifier constructor. ex: esn=DEVICE_12345 or ip=192.168.144.49
        """
        self.connected: bool = False
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in ["ip", "esn", "serial", "rae"]}
        self.device: DeviceIdentifier = DeviceIdentifier(**filtered_kwargs)
        self.plan_request: TestPlanRunRequest = TestPlanRunRequest()
        self.session: Session = Session()
        self.status_watchers = []
        self.ssl_context: Optional[ssl.SSLContext] = None

    def connect(self, broker: str):
        """Connect the session to an MQTT broker."""
        self.session.connect(broker)
        self.connected = True

    def get_test_plan(self, options: Optional[GetTestPlanRequestOptions] = None, type_: Optional[str] = None):
        """Get the test plan and store it internally."""
        plan_response = self.session.get_test_plan_for_device(self.device, options=options, type=type_)
        if plan_response.status != 200:
            raise ValueError(REQUEST_STATUS_FAILED)
        if len(plan_response.body.testcases) < 1:
            if plan_response.body.error is not None:
                raise ValueError(plan_response.body.error)
            else:
                raise ValueError(INCOMPLETE_PLAN_REQUEST_ERROR)

        self.plan_request = TestPlanRunRequest(target=self.device, testplan=plan_response.body)

    def run_tests(self, **kwargs):
        """
        Start the test plan and update watchers in the status_watchers list.

        An optional kwarg "batch" lets you tag this with a batch ID string.
        This would be used to run tests across multiple ESNs but have them reported as a single batch.

        Be sure to note the batch ID reported at log level WARNING if you want to find the batch without visiting the web UI.
        """
        if self.plan_request is None:
            self.get_test_plan()
        batch_id = kwargs.get("batch", None)
        # carefully copy to not modify the original plan on others
        self.plan_request: TestPlanRunRequest = copy.deepcopy(self.plan_request)

        if batch_id is not None:
            self.plan_request.testplan.batch_id = batch_id

        # stateful class already has a target - always use that instead
        self.plan_request.target = self.device

        def receive_update(client, userdata, packet):
            """
            Broadcast received updates to watchers.

            :param client:
            :param userdata:
            :param packet:
            :return:
            """
            logger.info(f"Received update on test plan progress on topic {packet.topic}: {str(packet.payload)}")
            [watcher.handle_progress_update(packet) for watcher in self.status_watchers]

            # we hand down the entire packet so the topic and payload can be inspected
            # when multiple devices are sending updates at once, this is how you tell which one is done during reporting
            if "running" in packet.payload and not packet.payload["running"]:
                [watcher.handle_run_complete(packet) for watcher in self.status_watchers]

        full_result = self.session.run_plan(self.plan_request)
        if full_result.status != 200:
            # usually timeout
            logger.error("The test plan run was not run:")
            logger.error(full_result.to_dict(casing=Casing.SNAKE))

        if full_result.body.error is not None:
            # explicit error message from the automator, but communicated
            logger.error("The test plan run was not run:")
            logger.error(full_result.to_dict(casing=Casing.SNAKE))

        if full_result.body.result_topic is not None:
            # Subscribe to topic returned as “resultTopic” to get test result stream
            self.session.subscribe(full_result.body.result_topic, receive_update)

    def cancel(self) -> HttpLikeCancelResponse:
        """Request a cancel of any running plan on a device."""
        return self.session.cancel_plan_for_device(self.device)

    def close(self):
        """Unsubscribe, stop handling, and disconnect from the remote broker."""
        self.session.destructor()

    def get_device_list(self) -> Optional[List[DeviceIdentifier]]:
        """
        List the devices on the remote RAE.

        If the target device has no RAE setting, it will return None.
        :return:
        """
        if self.device.rae is None:
            return None
        return self.session.get_device_list(self.device.rae)

    def is_esn_connected_to_eyepatch(self) -> Optional[bool]:
        """Is the configured device calibrated with an EyePatch?"""
        if self.device.rae is None:
            logger.error(
                "'is_esn_connected_to_eyepatch' requires a target RAE in the device object. This asks the EyePatch module on that "
                "RAE for the status of devices with EyePatch configurations. "
                "You can update the StatefulSession.device.rae variable to set it."
            )
            return None
        if self.device.esn is None or self.device.esn == "":
            logger.error(
                "'is_esn_connected_to_eyepatch' requires an ESN in the device. "
                "You can update the StatefulSession.device.esn variable to set it."
            )
            return None
        return self.session.is_esn_connected_to_eyepatch(self.device.rae, self.device.esn)

    def status(self, **kwargs) -> Optional[Tuple[HttpLikeStatusResponse, Dict]]:
        """Get the current status of our device from the automator."""
        if self.device.rae is None:
            logger.error(
                "'status' requires a target RAE in the device object. This asks the Automator on that RAE for the status of "
                "device runs. "
                "You can update the StatefulSession.device.rae variable to set it."
            )
            return None
        newargs = dict(device=self.device, **DeviceIdentifierTarget(target=self.device).to_dict())
        if kwargs.get("batch_id"):
            newargs["batch_id"] = kwargs["batch_id"]
        return self.session.status(self.device.rae, **newargs)

    def get_result_for_batch_id(self, batch_id: str) -> Optional[Tuple[HttpLikeStatusResponse, dict]]:
        if self.device.rae is None:
            logger.error(
                "'status' requires a target RAE in the device object. This asks the Automator on that RAE for the status of "
                "device runs. "
                "You can update the StatefulSession.device.rae variable to set it."
            )
            return None
        return self.session.get_result_for_batch_id(device=self.device, batch_id=batch_id)


@contextmanager
def stateful_session_mgr(**kwargs) -> Generator[StatefulSession, None, None]:
    """
    Conveniently makes and cleans up a StatefulSession.

    :param kwargs: rae (str), the broker to reach out to
    :return:
    """
    session = StatefulSession(**kwargs)
    try:
        if "configuration" not in kwargs:
            raise ValueError(
                "The stateful session manager call needs the keyword 'configuration' "
                "which indicates which broker and SSL configuration to use."
            )
        session.connect(kwargs["configuration"])
        yield session
    finally:
        session.close()

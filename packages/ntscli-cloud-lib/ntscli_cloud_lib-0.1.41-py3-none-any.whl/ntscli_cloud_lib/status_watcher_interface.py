#  Copyright (c) 2020 Netflix.
#  All rights reserved.
from kaiju_mqtt_py import MqttPacket


class StatusWatcherInterface:
    """Interface for objects that want to be notified of updates while using a StatefulSession."""

    def handle_progress_update(self, packet: MqttPacket) -> None:
        """
        Recieve updates of test runs.

        packet.payload is a dict that should be loadable as a CloudStatus object.

        :param packet:
        :return:
        """

    def handle_run_complete(self, packet: MqttPacket) -> None:
        """
        Recieve the final update of a test run.

        packet.payload is a dict that should be loadable as a CloudStatus object.

        :param packet:
        :return:
        """

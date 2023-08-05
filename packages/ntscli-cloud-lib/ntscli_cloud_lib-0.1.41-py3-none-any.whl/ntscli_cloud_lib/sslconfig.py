#  Copyright (c) 2020 Netflix.
#  All rights reserved.
#
import json
import logging
import ssl
from pathlib import Path
from typing import List
from typing import Optional


def reasons_for_file(x: Path) -> List[str]:
    """Generate and log verbal descriptions of why a file may not be valid."""
    reasons: List[str] = []
    if not x.exists():
        reasons.append(f"File {x} was missing")
    else:
        with x.open("r") as opened:
            first = opened.readline()
            if "PGP" in first:
                reasons.append(f"File {x} is still marked as PGP encrypted. It will need to be decrypted first.")
    for reason in reasons:
        logging.error(reason)
    return reasons


class SslConfig:
    """An MQTT connection configuration."""

    DEFAULT_PORT: int = 1883
    TLS_DEFAULT_PORT: int = 8883

    def __init__(self, name: str) -> None:
        """
        Create a configuration.

        This attempts to load some information about the configuration during construction,
        but can represent missing configuration directories.

        :param name: The name of the configuration or hostname of an insecure server.
        """
        self.dir = Path(name)
        self.rootcert: Path = self.dir / "rootca.crt"
        self.privatekey: Path = self.dir / "private.key"
        self.certificate: Path = self.dir / "cert.pem"
        self.overridefile: Path = self.dir / "host.json"
        self.certificate_id: Path = self.dir / "client.id"
        self.host: str = str(self.dir.parts[-1])
        self.port: int = self.TLS_DEFAULT_PORT if self.iscomplete() else self.DEFAULT_PORT
        self.scheme: str = "mqtt"
        self.protocol: List[str] = []

        if self.exists():
            # secure configurations must use ssl as the prefix
            self.scheme = "ssl"

        if self.overridefile.exists():
            try:
                overrides = json.loads(self.overridefile.read_text())
                self.host = overrides["host"] if "host" in overrides else str(self.dir.parts[-1])
                self.port = overrides["port"] if "port" in overrides else self.port
                self.protocol = overrides["alpnProtocol"] if "alpnProtocol" in overrides else None
                if self.certificate_id.exists():
                    self.certificate_id_topic_string = Path(self.certificate_id).read_text().strip()
            except json.JSONDecodeError:
                logging.error(f"Found invalid JSON in this file, ignoring it: {self.overridefile.as_posix()}")

    def __repr__(self) -> str:
        return self.dir.__repr__()

    def __str__(self) -> str:
        return self.scheme + "://" + self.host + ":" + str(self.port)

    def __bool__(self) -> bool:
        """Does the configuration directory for this object exist?"""
        return self.dir.exists()

    def exists(self) -> bool:
        """Does the configuration directory for this object exist?"""
        return self.dir.exists()

    def iscomplete(self) -> bool:
        """
        Is this configuration complete?

        This checks that all files are present and not PGP encoded.
        :return: True if complete, False if incomplete.
        """
        return len(self.explain()) == 0

    def explain(self) -> List[str]:
        """
        Examine and return a list of reasons a configuration is invalid.

        :return: Explanations of why a configuration is invalid.
        """
        files = [self.rootcert, self.privatekey, self.certificate, self.certificate_id]
        reasons = []
        for x in files:
            reasons.extend(reasons_for_file(x))
        return reasons

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Get the ssl context required for this configuration, if any.

        None will be returned if this configuration does not need an ssl context, like direct connections to localhost or other insecure
        brokers.

        Connecting to a secured broker has flavors:
            Secure,
            Secure on normal mqtt servers and ports, and
            Amazon special protocol for port 443 - see
        https://aws.amazon.com/blogs/iot/how-to-implement-mqtt-with-tls-client-authentication-on-port-443-from-client-devices-python/

        :return: None for insecure, loaded context for secure configurations
        """
        if not self.certificate.exists():
            # None is to indicate an insecure connection
            return None

        ssl_context = ssl.create_default_context()
        if self.protocol:
            ssl_context.set_alpn_protocols(self.protocol)
        ssl_context.load_verify_locations(cafile=self.rootcert)
        ssl_context.load_cert_chain(certfile=self.certificate, keyfile=self.privatekey)
        return ssl_context

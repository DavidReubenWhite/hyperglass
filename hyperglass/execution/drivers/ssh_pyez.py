"""Pyez-Specific Classes & Utilities.

"""

# Standard Library
import math
from typing import Iterable, Dict
from lxml.builder import E
from lxml import etree
import re

# Third Party
from jnpr.junos import Device

# Project
from hyperglass.log import log
from hyperglass.exceptions import (
    AuthError,
    ScrapeError,
    DeviceTimeout,
    UnsupportedDevice,
)
from hyperglass.configuration import params

# Local
from .ssh import SSHConnection

class PyEZConnection(SSHConnection):
    """Handle a device connection via PyEZ."""

    async def collect(self, host: str = None, port: int = None) -> Iterable:
        """Connect directly to a device.
        Directly connects to the router via Napalm library, returns the
        command output.
        """
        if host is not None:
            log.debug(
                "Connecting to {} via proxy {} [{}]",
                self.device.name,
                self.device.proxy.name,
                f"{host}:{port}",
            )
        else:
            log.debug("Connecting directly to {}", self.device.name)

        driver_kwargs = {
            "host": host or self.device._target,
            "port": port or self.device.port,
            "username": self.device.credential.username,
            "timeout": 90,
        }
        if self.device.credential._method == "password":
            # Use password auth if no key is defined.
            driver_kwargs[
                "passwd"
            ] = self.device.credential.password.get_secret_value()
        else:
            # Otherwise, use key auth.
            driver_kwargs["ssh_private_key_file"] = self.device.credential.key
            if self.device.credential._method == "encrypted_key":
                # If the key is encrypted, use the password field as the
                # private key password.
                driver_kwargs[
                    "passwd"
                ] = self.device.credential.password.get_secret_value()

        # log.debug('driver args: {}'.format(driver_kwargs))

        responses = ()

        try:
            with Device(**driver_kwargs) as dev:
                for query in self.query:
                    log.debug(query)
                    rpc = getattr(dev.rpc, query.get('rpc_name'))
                    response = rpc(**query.get('rpc_args'))
                    responses += (response,)
        except Exception as e:
            log.debug(e)

        if not responses:
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.name,
                proxy=None,
                error=params.messages.no_response,
            )

        return responses

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

        log.debug('driver args: {}'.format(driver_kwargs))

        responses = ()

        try:
            with Device(**driver_kwargs) as dev:
                for query in self.query:
                    log.debug(query)
                    rpc = getattr(dev.rpc, query.get('rpc_name'))
                    response = rpc(**query.get('rpc_args'))
                    log.debug(etree.tostring(response, encoding='unicode'))
                    # if 'traceroute' in query:
                    #     pattern = 'routing-instance ([A-Za-z0-9]+) ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+) wait 1 source ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)'
                    #     query_match = re.search(pattern, query)
                    #     ri = query_match.group(1)
                    #     dest = query_match.group(2)
                    #     source = query_match.group(3)

                    #     response = junos.traceroute(ttl='20', timeout='1', source=source, vrf=ri, destination=dest)
                    #     response = self.format_traceroute(response)
                    #     log.debug(response)
                    # else:
                    #     rpc = E("command", query)
                    #     response = junos.device._conn.rpc(rpc)
                    #     response = etree.tostring(response._NCElement__doc)
                    #     response = response.decode('utf-8')

                    responses += (response,)
        except Exception as e:
            log.debug(e)

        # formatting stuff
        # output_data = []
        # output_header = "{:<8} {:<35} {:<20} {:<20}".format('Hop','Host', 'Address', 'Probes') 
        # output_data.append(output_header)

        # output_lines = []
        # for hop, probes in trace['success'].items():
        #     output_line = ''
        #     output_line += "{:<8}".format(hop)
        #     hostname = ''
        #     address = ''
        #     for k, v in probes.items():
        #       rtts = []
        #       for probe_num, data in v.items():
        #         if data['ip_address'] != '*':
        #           # probe was successful
        #           rtts.append('{:.2f} ms'.format(data['rtt']))
        #           hostname = data['host_name']
        #           address = data['ip_address']
        #         else:
        #           # this should only be a *
        #           rtts.append('*')
        #       rtt_string = '  '.join(rtts)
        #       output_line += "{:<35}".format(hostname)
        #       output_line += "{:<20}".format(address)
        #       output_line += "{:<20}".format(rtt_string)
        #       output_lines.append(output_line)
        # formatted_response = '\n'.join(output_lines)  

        # for query in self.query:
        #     log.debug(query)
        #     response = dev.rpc.traceroute(
        #         wait='1', source='103.241.56.68', inet=True, routing_instance='Internet', host='8.8.8.8', ttl='20',
        #     )

            
        #     responses += (etree.tostring(response, encoding='unicode', pretty_print=True),)
        # dev.close()

        if not responses:
            raise ScrapeError(
                params.messages.connection_error,
                device_name=self.device.name,
                proxy=None,
                error=params.messages.no_response,
            )

        return responses

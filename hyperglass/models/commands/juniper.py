"""Juniper Command Model."""

# Third Party
from pydantic import StrictStr

# Local
from .common import CommandSet, CommandGroup
import json


class _IPv4(CommandSet):
    """Validation model for non-default dual afi commands."""

    bgp_route: StrictStr = 'show route protocol bgp table inet.0 {target} best detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table inet.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table inet.0 community {target}"
    ping: StrictStr = "ping inet {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet {target} wait 1 source {source}"


class _IPv6(CommandSet):
    """Validation model for non-default ipv4 commands."""

    bgp_route: StrictStr = 'show route protocol bgp table inet6.0 {target} best detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table inet6.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table inet6.0 community {target}"
    ping: StrictStr = "ping inet6 {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet6 {target} wait 2 source {source}"


class _VPNIPv4(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = 'show route protocol bgp table {vrf}.inet.0 {target} best detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table {vrf}.inet.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table {vrf}.inet.0 community {target}"
    ping: StrictStr = "ping inet routing-instance {vrf} {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet routing-instance {vrf} {target} wait 1 source {source}"


class _VPNIPv6(CommandSet):
    """Validation model for non-default ipv6 commands."""

    bgp_route: StrictStr = 'show route protocol bgp table {vrf}.inet6.0 {target} best detail | except Label | except Label | except "Next hop type" | except Task | except Address | except "Session Id" | except State | except "Next-hop reference" | except destinations | except "Announcement bits"'
    bgp_aspath: StrictStr = 'show route protocol bgp table {vrf}.inet6.0 aspath-regex "{target}"'
    bgp_community: StrictStr = "show route protocol bgp table {vrf}.inet6.0 community {target}"
    ping: StrictStr = "ping inet6 routing-instance {vrf} {target} count 5 source {source}"
    traceroute: StrictStr = "traceroute inet6 routing-instance {vrf} {target} wait 2 source {source}"


_structured = CommandGroup(
    ipv4_default=CommandSet(
        bgp_route=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': 'inet.0', 'destination': None, 'best': True, 'detail': True}}),
        bgp_aspath=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': 'inet.0', 'aspath-regex': None, 'detail': True}}),
        bgp_community="show route protocol bgp table inet.0 community {target} detail | display xml",
        ping="ping inet {target} count 5 source {source}",
        ping=json.dumps({'rpc_name': 'ping', 'rpc_args': {'inet': True, 'count': '5', 'source': None, 'host': None}}),
        traceroute="traceroute inet {target} wait 1 source {source}",
    ),
    ipv6_default=CommandSet(
        bgp_route=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': 'inet6.0', 'destination': None, 'best': True, 'detail': True}}),
        bgp_aspath=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': 'inet6.0', 'aspath-regex': None, 'detail': True}}),
        bgp_community="show route protocol bgp table inet6.0 community {target} detail | display xml",
        ping=json.dumps({'rpc_name': 'ping', 'rpc_args': {'inet6': True, 'count': '5', 'source': None, 'host': None}}),
        traceroute=json.dumps({'rpc_name': 'traceroute', 'rpc_args': {'wait': '2', 'inet6': True, 'dev_timeout': '90', 'ttl':'20', 'source': None, 'host': None}}),

    ),
    ipv4_vpn=CommandSet(
        bgp_route=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': None, 'destination': None, 'best': True, 'detail': True}}),
        bgp_aspath=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': None, 'aspath-regex': None, 'detail': True}}),
        bgp_community=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': None, 'community': None, 'detail': True}}),
        ping=json.dumps({'rpc_name': 'ping', 'rpc_args': {'inet': True, 'count': '5', 'source': None, 'routing_instance': None, 'host': None}}),
        traceroute=json.dumps({'rpc_name': 'traceroute', 'rpc_args': {'dev_timeout': '90', 'ttl':'20', 'wait':'1', 'source': None, 'routing_instance': None, 'host': None}}),
    ),
    ipv6_vpn=CommandSet(
        bgp_route=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': None, 'destination': None, 'best': True, 'detail': True}}),
        bgp_aspath=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': None, 'aspath-regex': None, 'detail': True}}),
        bgp_community=json.dumps({'rpc_name': 'get_route_information', 'rpc_args': {'dev_timeout': '90', 'protocol': 'bgp', 'table': None, 'community': None, 'detail': True}}),
        ping=json.dumps({'rpc_name': 'ping', 'rpc_args': {'inet6': True, 'count': '5', 'source': None, 'routing_instance': None, 'host': None}}),
        traceroute=json.dumps({'rpc_name': 'traceroute', 'rpc_args': {'wait': '2', 'inet6': True, 'dev_timeout': '90', 'ttl':'20', 'source': None, 'routing_instance': None, 'host': None}}),
    ),
)


class JuniperCommands(CommandGroup):
    """Validation model for default juniper commands."""

    ipv4_default: _IPv4 = _IPv4()
    ipv6_default: _IPv6 = _IPv6()
    ipv4_vpn: _VPNIPv4 = _VPNIPv4()
    ipv6_vpn: _VPNIPv6 = _VPNIPv6()

    def __init__(self, **kwargs):
        """Initialize command group, ensure structured fields are not overridden."""
        super().__init__(**kwargs)
        self.structured = _structured

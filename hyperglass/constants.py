"""Constant definitions used throughout the application."""

# Standard Library
from datetime import datetime

__name__ = "hyperglass"
__version__ = "1.0.4"
__author__ = "Matt Love"
__copyright__ = f"Copyright {datetime.now().year} Matthew Love"
__license__ = "BSD 3-Clause Clear License"

METADATA = (__name__, __version__, __author__, __copyright__, __license__)

MIN_PYTHON_VERSION = (3, 6)

MIN_NODE_VERSION = 14

TARGET_FORMAT_SPACE = ("huawei", "huawei_vrpv8")

TARGET_JUNIPER_ASPATH = ("juniper", "juniper_junos")

SUPPORTED_STRUCTURED_OUTPUT = ("juniper", "arista_eos")

STATUS_CODE_MAP = {"warning": 400, "error": 400, "danger": 500}

DNS_OVER_HTTPS = {
    "google": "https://dns.google/resolve",
    "cloudflare": "https://cloudflare-dns.com/dns-query",
}

PARSED_RESPONSE_FIELDS = (
    ("Prefix", "prefix", "left"),
    ("Active", "active", None),
    ("RPKI State", "rpki_state", "center"),
    ("AS Path", "as_path", "left"),
    ("Next Hop", "next_hop", "left"),
    ("Origin", "source_as", None),
    ("Weight", "weight", "center"),
    ("Local Preference", "local_preference", "center"),
    ("MED", "med", "center"),
    ("Communities", "communities", "center"),
    ("Originator", "source_rid", "right"),
    ("Peer", "peer_rid", "right"),
    ("Age", "age", "right"),
)

SUPPORTED_QUERY_FIELDS = ("query_location", "query_type", "query_target", "query_vrf")
SUPPORTED_QUERY_TYPES = (
    "bgp_route",
    "bgp_community",
    "bgp_aspath",
    "ping",
    "traceroute",
)

FUNC_COLOR_MAP = {
    "primary": "cyan",
    "secondary": "blue",
    "success": "green",
    "warning": "yellow",
    "error": "orange",
    "danger": "red",
}

TRANSPORT_REST = ("frr_legacy", "bird_legacy")

TRANSPORT_RPC = ("junos", "juniper", "junos_juniper")

SCRAPE_HELPERS = {
    "arista": "arista_eos",
    "ios": "cisco_ios",
    "juniper_junos": "juniper",
    "junos": "juniper",
    "mikrotik": "mikrotik_routeros",
    "tsnr": "tnsr",
}

DRIVER_MAP = {
    # TODO: Troubleshoot Arista with Scrapli, broken after upgrading to 2021.1.30.
    # "arista_eos": "scrapli", # noqa: E800
    "bird": "scrapli",
    "cisco_ios": "scrapli",
    "cisco_xe": "scrapli",
    "cisco_xr": "scrapli",
    "cisco_nxos": "scrapli",
    "juniper": "pyez",
    "tnsr": "scrapli",
    "frr": "scrapli",
    "frr_legacy": "hyperglass_agent",
    "bird_legacy": "hyperglass_agent",
}

RPC_VARIABLE_MAP = {
    "traceroute": {
        "vrf": "routing_instance",
        "target": "host",
        "source": "source"
    },
    "bgp_route": {
        "vrf": "table",
        "target": "destination"
    },
    "ping": {
        "vrf": "routing_instance",
        "target": "host",
        "source": "source"
    },
    "bgp_aspath": {
        "vrf": "table",
        "target": "aspath-regex",
    },
}

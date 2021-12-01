"""Parse Juniper XML Response to Structured Data."""

# Standard Library
import re
from typing import Dict, List, Sequence, Generator

# Third Party
import xmltodict
from pydantic import ValidationError
from lxml.etree import iselement, tostring

# Project
from hyperglass.log import log
from hyperglass.exceptions import ParsingError
from hyperglass.models.parsing.juniper import JuniperRoute

REMOVE_PATTERNS = (
    # The XML response can a CLI banner appended to the end of the XML
    # string. For example:
    # ```
    # <rpc-reply>
    # ...
    # <cli>
    #   <banner>{master}</banner>
    # </cli>
    # </rpc-reply>
    #
    # {master} noqa: E800
    # ```
    #
    # This pattern will remove anything inside braces, including the braces.
    r"\{.+\}",
)


def clean_xml_output(output: str) -> str:
    """Remove Juniper-specific patterns from output."""

    def scrub(lines: List[str]) -> Generator[str, None, None]:
        """Clean & remove each pattern from each line."""
        for pattern in REMOVE_PATTERNS:
            for line in lines:
                # Remove the pattern & strip extra newlines
                scrubbed = re.sub(pattern, "", line.strip())
                # Only return non-empty and non-newline lines
                if scrubbed and scrubbed != "\n":
                    yield scrubbed

    lines = scrub(output.splitlines())

    return "\n".join(lines)

def find_txt(xml_tree, path, default=''):
    """
    Extracts the text value from an XML tree, using XPath.
    In case of error, will return a default value.
    :param xml_tree: the XML Tree object. Assumed is <type 'lxml.etree._Element'>.
    :param path:     XPath to be applied, in order to extract the desired data.
    :param default:  Value to be returned in case of error.
    :return: a str value.
    """
    value = ''
    try:
        xpath_applied = xml_tree.xpath(path)  # will consider the first match only
        if len(xpath_applied) and xpath_applied[0] is not None:
            xpath_result = xpath_applied[0]
            if isinstance(xpath_result, type(xml_tree)):
                value = xpath_result.text.strip()
            else:
                value = xpath_result
        else:
            value = default
    except Exception:  # in case of any exception, returns default
        value = default
    return value

def convert(to, who, default=u''):
    """
    Converts data to a specific datatype.
    In case of error, will return a default value.
    :param to:      datatype to be casted to.
    :param who:     value to cast.
    :param default: value to return in case of error.
    :return: a str value.
    """
    if who is None:
        return default
    try:
        return to(who)
    except:  # noqa
        return default

def parse_juniper_ping(output: Sequence) -> str:
    ping_result = {'probes': {}}

    for i, response in enumerate(output):
        target_host = find_txt(response, 'target-host', '*')
        target_ip = find_txt(response, 'target-ip', '*')
        source = find_txt(response, 'source', '*')
        packet_size = convert(
            int, find_txt(response, 'packet-size', 0)
        )
        layer_2_size = packet_size + 28

        probes_summary = response.find('probe-results-summary')
        probes_sent = find_txt(probes_summary, 'probes-sent', '0')
        responses_received = find_txt(probes_summary, 'responses-received', '0')
        packet_loss = find_txt(probes_summary, 'packet-loss', '0')
        rtt_min = convert(
            float, find_txt(probes_summary, 'rtt-minimum', 0)
        ) * 1e-3 # ms
        rtt_max = convert(
            float, find_txt(probes_summary, 'rtt-maximum', 0)
        ) * 1e-3
        rtt_avg = convert(
            float, find_txt(probes_summary, 'rtt-average', 0)
        ) * 1e-3
        rtt_stddev = convert(
            float, find_txt(probes_summary, 'rtt-stddev', 0)
        ) * 1e-3

        probes = response.findall('probe-result')
        for probe in probes:
            sequence_no = convert(
                int, find_txt(probe, 'probe-index', 0)
            )
            address = find_txt(probe, 'ip-address', '*')
            response_size = find_txt(probe, 'response-size', 0)
            rtt = convert(
                float, find_txt(probe, 'rtt', 0)
            ) * 1e-3 # ms
            ttl = find_txt(probe, 'time-to-live', 0)
            ping_result['probes'][sequence_no - 1] = {
                'sequence_no': sequence_no,
                'address': address,
                'response_size': response_size,
                'rtt': rtt,
                'ttl': ttl
            }
    output_header = ["PING {} ({}) {}({}) bytes of data.".format(
        target_host, target_ip, packet_size, layer_2_size
    )]
    output_lines = []

    for _, probe in ping_result['probes'].items():
        output_line = "{} bytes from {}: icmp_seq={} ttl={} time={:.1f} ms".format(
            probe['response_size'], probe['address'], probe['sequence_no'], probe['ttl'], probe['rtt']
        )
        output_lines.append(output_line)

    output_footer = ["--- {} ping statistics ---\n{} packets transmitted, {} received, {}% packet loss\nrtt min/avg/max/mdev = {:.3f}/{:.3f}/{:.3f}/{:.3f} ms".format(
        target_host, probes_sent, responses_received, packet_loss, rtt_min, rtt_avg, rtt_max, rtt_stddev)
    ]
    return '\n'.join(output_header + output_lines + output_footer)

def parse_juniper_traceroute(output: Sequence) -> str:


    traceroute_result = {}
    traceroute_result['success'] = {}

    for i, response in enumerate(output):
        for hop in response.findall('hop'):
            ttl_value = convert(
                int, find_txt(hop, 'ttl-value'), 1)
            if ttl_value not in traceroute_result['success']:
                traceroute_result['success'][ttl_value] = {'probes': {}}
            for probe in hop.findall('probe-result'):
                probe_index = convert(
                    int, find_txt(probe, 'probe-index', 0))
                ip_address = convert(
                    str, find_txt(probe, 'ip-address', '*'))
                host_name = find_txt(probe, 'host-name', '*')
                rtt = convert(
                    float, find_txt(probe, 'rtt'), 0) * 1e-3  # ms
                traceroute_result['success'][ttl_value]['probes'][probe_index] = {
                    'ip_address': ip_address,
                    'host_name': host_name,
                    'rtt': rtt
                }

    output_header = ["{:<7} {:<34} {:<19} {:<20}".format('Hop','Host', 'Address', 'Probes')]
    output_lines = []
    for hop, probes in traceroute_result['success'].items():
        output_line = ''
        output_line += "{:<8}".format(hop)
        hostname = ''
        address = ''
        print(hop)
        print(probes)
        for k, v in probes.items():
            rtts = []
            for probe_num, data in v.items():
                if data['ip_address'] != '*':
                    # probe was successful
                    rtts.append(('{:.2f} ms'.format(data['rtt']).ljust(10)))
                    hostname = data['host_name']
                    address = data['ip_address']
                else:
                    # this should only be a *
                    rtts.append('*'.ljust(10))
            rtt_string = '  '.join(rtts)
            output_line += "{:<35}".format(hostname)
            output_line += "{:<20}".format(address)
            output_line += "{:<20}".format(rtt_string)
            output_lines.append(output_line)
    return '\n'.join(output_header + output_lines)

def parse_juniper(output: Sequence) -> Dict:  # noqa: C901
    """Parse a Juniper BGP XML response. Response can either be XML string or ElementTree"""
    data = {}

    for i, response in enumerate(output):
        if iselement(response):
            response = tostring(response, encoding='unicode')
        cleaned = clean_xml_output(response)

        try:
            parsed = xmltodict.parse(
                cleaned, force_list=("rt", "rt-entry", "community")
            )

            log.debug("Initially Parsed Response: \n{}", parsed)

            if "rpc-reply" in parsed.keys():
                if "xnm:error" in parsed["rpc-reply"]:
                    if "message" in parsed["rpc-reply"]["xnm:error"]:
                        err = parsed["rpc-reply"]["xnm:error"]["message"]
                        raise ParsingError('Error from device: "{}"', err)

                parsed_base = parsed["rpc-reply"]["route-information"]
            elif "route-information" in parsed.keys():
                parsed_base = parsed["route-information"]
                log.debug('doing stuff')

            if "route-table" not in parsed_base:
                log.debug('no route-table')
                return data

            if "rt" not in parsed_base["route-table"]:
                log.debug('no rt')
                log.debug(parsed_base["route-table"])
                return data
            log.debug('we are here')
            parsed = parsed_base["route-table"]
            log.debug(parsed)
            validated = JuniperRoute(**parsed)
            log.debug(validated)
            serialized = validated.serialize().export_dict()
            log.debug(serialized)
            if i == 0:
                data.update(serialized)
            else:
                data["routes"].extend(serialized["routes"])

        except xmltodict.expat.ExpatError as err:
            log.critical(str(err))
            raise ParsingError("Error parsing response data") from err

        except KeyError as err:
            log.critical("{} was not found in the response", str(err))
            raise ParsingError("Error parsing response data")

        except ValidationError as err:
            log.critical(str(err))
            raise ParsingError(err.errors())

    return data

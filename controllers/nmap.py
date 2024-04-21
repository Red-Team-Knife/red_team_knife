import threading
import subprocess, os, json, shutil, time
import nmap3
from utils.commands import build_command_string
from controllers.controller_thread import Controller, CommandThread
import xmltodict

TOOL_NAME = "Nmap"
LIST_SCAN = "list_scan"
NO_PORT_SCAN = "no_port_scan"
SKIP_DISCOVERY = "skip_discovery"
PING_TCP_SYN = "ping_tcp_syn"
PING_TCP_ACK = "ping_tcp_ack"
PING_UDP = "ping_udp"
PING_SCTP_INIT = "ping_sctp_init"
ICMP_ECHO = "icmp_echo"
ICMP_TIMESTAMP = "icmp_timestamp"
ICMP_MASK = "icmp_mask"
IP_PROTOCOL_PING = "ip_protocol_ping"
DISABLE_DNS = "disable_dns"
ALWAYS_RESOLVE_DNS = "always_resolve_dns"
TRACEROUTE = "traceroute"
TCP_SYN_SCAN = "tcp_syn_scan"
CONNECT_SCAN = "connect_scan"
ACK_SCAN = "ack_scan"
WINDOW_SCAN = "window_scan"
MAIMON_SCAN = "maimon_scan"
UDP_SCAN = "udp_scan"
TCP_NULL_SCAN = "tcp_null_scan"
FIN_SCAN = "fin_scan"
XMAS_SCAN = "xmas_scan"
IDLE_SCAN = "idle_scan"
IDLE_SCAN_ZOMBIE_HOST = "idle_scan_zombie_host"
SCTP_SCAN = "sctp_scan"
COOKIE_ECHO_SCAN = "cookie_echo_scan"
IP_PROTOCOL_SCAN = "ip_protocol_scan"
FTP_BOUNCE_SCAN = "ftp_bounce_scan"
FTP_BOUNCE_HOST = "ftp_bounce_host"
PORT_RANGE = "port_range"
EXCLUDE_PORTS = "exclude_ports"
FAST_MODE = "fast_mode"
SET_SEQUENTIALLY = "set_sequentially"
TOP_PORTS = "top_ports"
PORT_RATIO = "port_ratio"
DISCOVER_INFO_PORTS = "discover_info_ports"
VERSION_INTENSITY = "version_intensity"
OS_DETECTION = "os_detection"
LIMIT_OS = "limit_os"
GUESS_OS = "guess_os"
MIN_RATE = "min_rate"
MAX_RATE = "max_rate"
SCAN_DELAY = "scan_delay"
HOST_TIMEOUT = "host_timeout"
MAX_RETRIES = "max_retries"
MIN_PARALLEL = "min_parallel"
MAX_PARALLEL = "max_parallel"
INITIAL_PARALLEL = "initial_parallel"
MIN_HOSTGROUP = "min_hostgroup"
MAX_HOSTGROUP = "max_hostgroup"
MIN_RTT_TIMEOUT = "min_roundtrip_time_timeout"
MAX_RTT_TIMEOUT = "max_roundtrip_time_timeout"
INITIAL_RTT_TIMEOUT = "initial_roundtrip_time_timeout"
TIMING_TEMPLATE = "timing_template"
TINY_PACKETS = "tiny_packets"
CLOAK_DECOY = "cloak_decoy"
SPOOF_SOURCE = "spoof_source"
INTERFACE = "interface"
SOURCE_PORT = "source_port"
SET_PROXIES = "set_proxies"
SET_HEX_PAYLOAD = "set_hex_payload"
SET_ASCII_PAYLOAD = "set_ascii_payload"
SET_RANDOM_DATA = "set_random_data"
SET_IP_OPTIONS = "set_ip_options"
SET_TTL = "set_ttl"
SPOOF_MAC = "spoof_mac"
BAD_SUM = "bad_sum"
SET_IPV6 = "set_ipv6"
FULLY_PRIVILAGED = "fully_privileged"
POORLY_PRIVILAGED = "poorly_privileged"
PRINT_ONLY_OPEN = "print_only_open"
RADIO_SCAN_TYPE = "radio_scan_type"
RADIO_USER_PRIVILAGE = "radio_user_privilage"
RADIO_DNS_RESOLUTION = "radio_dns_resolution"

TEMP_FILE_NAME = "tmp/nmap-temp"
RUNNING_MESSAGE = "Running Nmap with command: "


scan_options = [
    ("Set List Scan", "checkbox", LIST_SCAN, ""),
    ("Disable Port Scan", "checkbox", NO_PORT_SCAN, ""),
    ("Skip Host Discovery", "checkbox", SKIP_DISCOVERY, ""),
    ("Ping TCP SYN", "text", PING_TCP_SYN, "80, 20, 500"),
    ("Ping TCP ACK", "text", PING_TCP_ACK, "80, 20, 500"),
    ("Ping UDP", "text", PING_UDP, "80, 20, 500"),
    ("Ping SCTP INIT", "text", PING_SCTP_INIT, "80, 20, 500"),
    ("Ping ICMP echo", "checkbox", ICMP_ECHO, ""),
    ("Ping ICMP Timestamp", "checkbox", ICMP_TIMESTAMP, ""),
    ("Ping ICMP Address mask", "checkbox", ICMP_MASK, ""),
    ("IP Protocol Ping", "text", IP_PROTOCOL_PING, "IP-in-IP, IGMP"),
    ("Disable DNS Resolution", "radio", DISABLE_DNS, RADIO_DNS_RESOLUTION),
    ("Enable Total Dns Resolution", "radio", ALWAYS_RESOLVE_DNS, RADIO_DNS_RESOLUTION),
    ("Enable Traceroute", "checkbox", TRACEROUTE, ""),
    ("TCP SYN Scan", "radio", TCP_SYN_SCAN, RADIO_SCAN_TYPE),
    ("Connect() Scan", "radio", CONNECT_SCAN, RADIO_SCAN_TYPE),
    ("ACK Scan", "radio", ACK_SCAN, RADIO_SCAN_TYPE),
    ("Window Scan", "radio", WINDOW_SCAN, RADIO_SCAN_TYPE),
    ("Maimon Scan", "radio", MAIMON_SCAN, RADIO_SCAN_TYPE),
    ("UDP Scan", "radio", UDP_SCAN, RADIO_SCAN_TYPE),
    ("TCP Null Scan", "radio", TCP_NULL_SCAN, RADIO_SCAN_TYPE),
    ("FIN Scan", "radio", FIN_SCAN, RADIO_SCAN_TYPE),
    ("Xmas Scan", "radio", XMAS_SCAN, RADIO_SCAN_TYPE),
    ("Idle Scan", "radio", IDLE_SCAN, RADIO_SCAN_TYPE),
    ("", "text", IDLE_SCAN_ZOMBIE_HOST, "host[:probeport]"),
    ("SCTP INIT Scan", "radio", SCTP_SCAN, RADIO_SCAN_TYPE),
    ("Cookie-Echo Scan", "radio", COOKIE_ECHO_SCAN, RADIO_SCAN_TYPE),
    ("IP Protocol Scan", "radio", IP_PROTOCOL_SCAN, RADIO_SCAN_TYPE),
    ("FTP Bounce Scan", "radio", FTP_BOUNCE_SCAN, RADIO_SCAN_TYPE),
    ("", "text", FTP_BOUNCE_HOST, "FTP Relay Host"),
    ("Port Range", "number", PORT_RANGE, "22, 21-25"),
    ("Exclude Ports", "number", EXCLUDE_PORTS, "22, 21-25"),
    ("Fast Mode", "checkbox", FAST_MODE, ""),
    ("Set Sequentially Scan", "checkbox", SET_SEQUENTIALLY, ""),
    ("Top Ports", "number", TOP_PORTS, ""),
    ("Set Port Ratio", "number", PORT_RATIO, ""),
    ("Discover Services Info for Ports", "checkbox", DISCOVER_INFO_PORTS, ""),
    ("Set Intensity Level", "number", VERSION_INTENSITY, "0(Light), 9 (Tty all probes)"),
    ("Enable Os Detection", "checkbox", OS_DETECTION, ""),
    ("Limit OS Detection to Promising Targets", "checkbox", LIMIT_OS, ""),
    ("Guess OS more Aggressively", "checkbox", GUESS_OS, ""),
    ("Set Min Send Rate", "number", MIN_RATE, "<number> per second"),
    ("Set Max Send Rate", "number", MAX_RATE, "<number> per second"),
    ("Set Scan delay", "number", SCAN_DELAY, "5s, 10m, 3h"),
    ("Set Host Timeout", "number", HOST_TIMEOUT, "5s, 10m, 3h"),
    ("Set Max Number of Retries", "number", MAX_RETRIES, "10"),
    ("Set Min Parallelism", "number", MIN_PARALLEL, "10"),
    ("Set Max Parallelism", "number", MAX_PARALLEL, "10"),
    ("Set Min Hostgroup", "number", MIN_HOSTGROUP, "10"),
    ("Set Max Hostgroup", "number", MAX_HOSTGROUP, "10"),
    ("Set Min Roundtrip Time Timeout", "number", MIN_RTT_TIMEOUT, "5s, 10m, 3h"),
    ("Set Max Roundtrip Time Timeout", "number", MAX_RTT_TIMEOUT, "5s, 10m, 3h"),
    ("Set Initial Roundtrip Time Timeout", "number", INITIAL_RTT_TIMEOUT, "5s, 10m, 3h"),
    ("Set Timing Template", "number", TIMING_TEMPLATE, "0-5 (high is faster)"),
    ("Use Tiny Packets", "checkbox", TINY_PACKETS, ""),
    ("Cloak a Scan with Decoys", "text", CLOAK_DECOY, ""),
    ("Spoof Source Address", "text", SPOOF_SOURCE, "123.123.123.123"),
    ("Use Interface", "text", INTERFACE, ""),
    ("Use Given port number", "number", SOURCE_PORT, "80"),
    ("Set Proxies", "text", SET_PROXIES, "Proxy URL"),
    ("Set Payload", "number", SET_HEX_PAYLOAD, "Hex string"),
    ("Set ASCII String Payload", "text", SET_ASCII_PAYLOAD, "abcde"),
    ("Append Random Data", "number", SET_RANDOM_DATA, "Data Lenght"),
    ("Set Specified IP Options", "text", SET_IP_OPTIONS, "Options"),
    ("Set IP Time To Live", "number", SET_TTL, "5s, 10m, 3h"),
    ("Spoof Your Mac Address", "number", SPOOF_MAC, "mac address/prefix/vendor name"),
    ("Send packets with a bogus TCP/UDP/SCTP checksum", "text", BAD_SUM, ""),
    ("Enable IPv6 Scan", "checkbox", SET_IPV6, ""),
    ("Set Fully Privileged user", "radio", FULLY_PRIVILAGED, RADIO_USER_PRIVILAGE),
    ("Set Poorly Privileged user", "radio", POORLY_PRIVILAGED, RADIO_USER_PRIVILAGE),
    ("Show Only Open or Possilbly Open Ports", "checkbox", PRINT_ONLY_OPEN, ""),
]

class NmapController(Controller):
    def __init__(self):       
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.tool_name = TOOL_NAME

    def run(self, target, options:dict):
        self.last_scan_result = None

        command = [
            "nmap",
            "-oX",
            TEMP_FILE_NAME,
        ]

        # composite settings
        # host discovery
        if options.get(LIST_SCAN, False):
            command.append("-sL")            
        if options.get(NO_PORT_SCAN, False):
            command.append("-sn")
        if options.get(SKIP_DISCOVERY, False):
            command.append("-Pn")
        if options.get(PING_TCP_SYN, False):
            command.append("-PS")
            command.append('[' + ','.join(map(str, options[PING_TCP_SYN])) + ']')
        if options.get(PING_TCP_ACK, False):
            command.append("-PA")
            command.append('[' + ','.join(map(str, options[PING_TCP_ACK])) + ']')
        if options.get(PING_UDP, False):
            command.append("-PU")
            command.append('[' + ','.join(map(str, options[PING_UDP])) + ']')
        if options.get(PING_SCTP_INIT, False):
            command.append("-PY")
            command.append('[' + ','.join(map(str, options[PING_SCTP_INIT])) + ']')
        if options.get(ICMP_ECHO, False):
            command.append("-PE")         
        if options.get(ICMP_TIMESTAMP, False):
            command.append("-PP")
        if options.get(ICMP_MASK, False):
            command.append("-PM")
        if options.get(IP_PROTOCOL_PING, False):
            command.append("-PO")
            command.append('[' + ','.join(map(str, options[IP_PROTOCOL_PING])) + ']')
        if options.get(RADIO_DNS_RESOLUTION, False):
            if options[RADIO_DNS_RESOLUTION] == DISABLE_DNS:
                command.append("-n")
            elif options[RADIO_DNS_RESOLUTION] == ALWAYS_RESOLVE_DNS:
                command.append("-R")
        if options.get(TRACEROUTE, False):
            command.append("--traceroute")

        # scan techniques    
        if options.get(RADIO_SCAN_TYPE, False):
            if options[RADIO_SCAN_TYPE] == TCP_SYN_SCAN:
                command.append("-sS")
            elif options[RADIO_SCAN_TYPE] == CONNECT_SCAN:
                command.append("-sT")
            elif options[RADIO_SCAN_TYPE] == ACK_SCAN:
                command.append("-sA")
            elif options[RADIO_SCAN_TYPE] == WINDOW_SCAN:
                command.append("-sW")
            elif options[RADIO_SCAN_TYPE] == MAIMON_SCAN:
                command.append("-sM")
            elif options[RADIO_SCAN_TYPE] == UDP_SCAN:
                command.append("-sU")
            elif options[RADIO_SCAN_TYPE] == TCP_NULL_SCAN:
                command.append("-sN")
            elif options[RADIO_SCAN_TYPE] == FIN_SCAN:
                command.append("-sF")
            elif options[RADIO_SCAN_TYPE] == XMAS_SCAN:
                command.append("-sX")
            elif options[RADIO_SCAN_TYPE] == IDLE_SCAN:
                if options.get(IDLE_SCAN_ZOMBIE_HOST, False):
                    command.append("-sF")
                    command.append(options[IDLE_SCAN_ZOMBIE_HOST])
            elif options[RADIO_SCAN_TYPE] == SCTP_SCAN:
                command.append("-sY")
            elif options[RADIO_SCAN_TYPE] == COOKIE_ECHO_SCAN:
                command.append("-sZ")
            elif options[RADIO_SCAN_TYPE] == IP_PROTOCOL_SCAN:
                command.append("-sO")
            elif options[RADIO_SCAN_TYPE] == FTP_BOUNCE_SCAN:
                if options.get(FTP_BOUNCE_HOST, False):
                    command.append("b")
                    command.append(options[FTP_BOUNCE_HOST])

        # port specification and scan order
        if options.get(PORT_RANGE, False):
            command.append("-p")
            command.append(options[PORT_RANGE])
        if options.get(EXCLUDE_PORTS, False):
            command.append("--exclude-ports")
            command.append(options[EXCLUDE_PORTS])
        if options.get(FAST_MODE, False):
            command.append("-F")
        if options.get(SET_SEQUENTIALLY, False):
            command.append("-r")
        if options.get(TOP_PORTS, False):
            command.append("--top-ports")
            command.append(options[TOP_PORTS])
        if options.get(PORT_RATIO, False):
            command.append("--port-ratio")
            command.append(options[PORT_RATIO])
        
        # service/version detection
        if options.get(DISCOVER_INFO_PORTS, False):
            command.append("-sV")
        if options.get(VERSION_INTENSITY, False):
            command.append("--version-intensity")
            command.append(options[VERSION_INTENSITY])
        
        # os detection
        if options.get(OS_DETECTION, False):
            command.append("-O")
        if options.get(LIMIT_OS, False):
            command.append("--osscan-limit")
        if options.get(GUESS_OS, False):
            command.append("--osscan-guess")

        # timing and performance
        if options.get(MIN_RATE, False):
            command.append("--min-rate")
            command.append(options[MIN_RATE])
        if options.get(MAX_RATE, False):
            command.append("--max-rate")
            command.append(options[MAX_RATE])
        if options.get(SCAN_DELAY, False):
            command.append("--scan-delay")
            command.append(options[SCAN_DELAY])
        if options.get(HOST_TIMEOUT, False):
            command.append("--host-timeout")
            command.append(options[HOST_TIMEOUT])
        if options.get(MAX_RETRIES, False):
            command.append("--max-tries")
            command.append(options[MAX_RETRIES])
        if options.get(MIN_PARALLEL, False):
            command.append("--min-parallelism")
            command.append(options[MIN_PARALLEL])
        if options.get(MAX_PARALLEL, False):
            command.append("--max-parallelism")
            command.append(options[MAX_PARALLEL])
        if options.get(MIN_HOSTGROUP, False):
            command.append("--min-hostgroup")
            command.append(options[MIN_HOSTGROUP])
        if options.get(MAX_HOSTGROUP, False):
            command.append("--max-hostgroup")
            command.append(options[MAX_HOSTGROUP])
        if options.get(MIN_RTT_TIMEOUT, False):
            command.append("--min-rtt-timeout")
            command.append(options[MIN_RTT_TIMEOUT])
        if options.get(MAX_RTT_TIMEOUT, False):
            command.append("--max-rtt-timeout")
            command.append(options[MAX_RTT_TIMEOUT])
        if options.get(INITIAL_RTT_TIMEOUT, False):
            command.append("--initial-rtt-timeout")
            command.append(options[INITIAL_RTT_TIMEOUT])
        if options.get(TIMING_TEMPLATE, False):
            command.append("-T")
            command.append(options[TIMING_TEMPLATE])

        # firewall/ids evasion and spoofing
        if options.get(TINY_PACKETS, False):
            command.append("-f")
        if options.get(CLOAK_DECOY, False):
            command.append("-D")
            command.append(','.join(map(str, options[CLOAK_DECOY])))
        if options.get(SPOOF_SOURCE, False):
            command.append("-S")
            command.append(options[SPOOF_SOURCE])
        if options.get(INTERFACE, False):
            command.append("-e")
            command.append(options[INTERFACE])
        if options.get(SOURCE_PORT, False):
            command.append("--source-port")
            command.append(options[SOURCE_PORT])
        if options.get(SET_PROXIES, False):
            command.append("--proxies")
            command.append(','.join(map(str, options[SET_PROXIES])))
        if options.get(SET_HEX_PAYLOAD, False):
            command.append("--data")
            command.append(options[SET_HEX_PAYLOAD])
        if options.get(SET_ASCII_PAYLOAD, False):
            command.append("--data-string")
            command.append(options[SET_ASCII_PAYLOAD])
        if options.get(SET_RANDOM_DATA, False):
            command.append("--data-lenght")
            command.append(options[SET_RANDOM_DATA])
        if options.get(SET_IP_OPTIONS, False):
            command.append("--ip-options")
            command.append(options[SET_IP_OPTIONS])
        if options.get(SET_TTL, False):
            command.append("--ttl")
            command.append(options[SET_TTL])
        if options.get(SPOOF_MAC, False):
            command.append("--spoof-mac")
            command.append(options[SPOOF_MAC])
        if options.get(BAD_SUM, False):
            command.append("--badsum")
            command.append(options[SOURCE_PORT])

        # miscellaneus
        if options.get(SET_IPV6, False):
            command.append("-6")
        if options.get(RADIO_USER_PRIVILAGE, False):
            if options[RADIO_USER_PRIVILAGE] == FULLY_PRIVILAGED:
                command.append("--privileged")
            else:
                command.append("--unprivileged")

        # output
        if options.get(PRINT_ONLY_OPEN, False):
            command.append("--open")

        # set target
        command.append(target)

        command_string = build_command_string(command)

        print(RUNNING_MESSAGE + command_string[:-1])

        # create temp file to save scan details


        class NmapCommandThread(CommandThread):
            def run(self):
                super().run()
                #TODO controlla se il file viene creato subito o solo dopo la fine dello scan
                if self._stop_event.is_set():
                    try:
                        os.remove(TEMP_FILE_NAME)
                    except:
                        print("Couldn't remove temp Nmap file.")

        self.thread = NmapCommandThread(command, self)
        self.thread.start()

    def __format_result__(self):

        if not self.last_scan_result:
            json_objects = ''

            with open(TEMP_FILE_NAME, "r") as file:
                # converting xml to dict
                xml_dict = xmltodict.parse(file.read())

                json_objects += json.dumps(xml_dict)

            os.remove(TEMP_FILE_NAME)

            self.last_scan_result = json_objects

        return self.last_scan_result
    

    def restore_last_scan(self):
        type = self.last_scan_result['type']
        if type == "top":
            return self.__format_top_result__(self.last_scan_result)
        elif type == "dns":
            return self.__format_dns_result__(self.last_scan_result)
        elif type == "list":
            return self.__format_list_result__(self.last_scan_result)
        elif type == "os":
            return self.__format_os_result__(self.last_scan_result)
        elif type == "version":
            return self.__format_version_result__(self.last_scan_result)
        else:
            return self.format_error()

    def __format_list_result__(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Ip</th>
                                <th>Hostname</th>
                                <th>Type</th>
                            </tr>
                        """

        ips = self.__remove_unnecessary_keys__(scan_result.keys())
        print('ips', ips)

        # Loop through each IP address
        for ip in ips:
            print(ip)
            for hostname in scan_result[ip]["hostname"]:
                html_output += f"""
                    <tr>
                        <td>{ip}</td>
                        <td>{hostname['name']}</td>
                        <td>{hostname['type']}</td>
                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __format_os_result__(self, scan_result):
        print(scan_result)
        html_output = """
                        <table>
                            <tr>
                                <th>Address</th>
                                <th>Os match</th>
                                <th>Line</th>
                                <th>Accuracy</th>
                                <th>Os family</th>
                                <th>Type</th>
                                <th>Vendor</th>
                            </tr>
                        """
        ips = scan_result.keys() - ["runtime", "stats", "task_results", "type"]
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for os_info in scan_result[ip]["osmatch"]:
                html_output += f"""
                    <tr>
                        <td>{ip}</td>
                        <td>{os_info['name']}</td>
                        <td>{os_info['line']}</td>
                        <td>{os_info['osclass']['accuracy']}</td>
                        <td>{os_info['osclass']['osfamily']}</td>
                        <td>{os_info['osclass']['type']}</td>
                        <td>{os_info['osclass']['vendor']}</td>
                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __format_version_result__(self, scan_result):
        print(scan_result)
        html_output = """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Port</th>
                                <th>Protocol</th>
                                <th>Status</th>
                                <th>Service Name</th>
                                <th>Conf</th>
                                <th>Extra info</th>
                                <th>Method</th>
                                <th>Os type</th>
                                <th>Product</th>
                                <th>Tunnel</th>
                                <th>Version</th>
                            </tr>
                        """

        ips = scan_result.keys() - ["runtime", "stats", "task_results"]
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for port_info in scan_result[ip]["ports"]:
                html_output += f"""
                    <tr class="{'' if port_info['state'] != 'open' else 'open'}">
                        <td>{', '.join(host['name'] for host in scan_result[ip]['hostname'])}</td>
                        <td>{port_info['portid']}</td>
                        <td>{port_info['protocol']}</td>
                        <td>{port_info['state']}</td>
                        <td>{port_info['service']['name']}</td>
                        <td>{port_info['service'].get('conf', '')}</td>
                        <td>{port_info['service'].get('extrainfo', '')}</td>
                        <td>{port_info['service'].get('method', '')}</td>
                        <td>{port_info['service'].get('ostype', '')}</td>
                        <td>{port_info['service'].get('product', '')}</td>
                        <td>{port_info['service'].get('tunnel', '')}</td>
                        <td>{port_info['service'].get('version', '')}</td>

                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __format_dns_result__(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Address</th>
                            </tr>
                        """

        for address in scan_result:
            html_output += f"""
                <tr>
                    <td>{address['hostname']}</td>
                    <td>{address['address']}</td>
                </tr>
            
                """
        html_output += "</table>"
        return html_output

    def __format_top_result__(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Port</th>
                                <th>Protocol</th>
                                <th>Status</th>
                                <th>Service</th>
                            </tr>
                        """

        ips = self.__remove_unnecessary_keys__(scan_result.keys())
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for port_info in scan_result[ip]["ports"]:
                html_output += f"""
                    <tr class="{'' if port_info['state'] != 'open' else 'open'}">
                        <td>{', '.join(host['name'] for host in scan_result[ip]['hostname'])}</td>
                        <td>{port_info['portid']}</td>
                        <td>{port_info['protocol']}</td>
                        <td>{port_info['state']}</td>
                        <td>{port_info['service']['name']}</td>
                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __remove_unnecessary_keys__(self, keys):
        return keys - ["runtime", "stats", "task_results", "type"]
import os, json, shutil
from loguru import logger as l
from threading import Thread
import time
from utils.utils import remove_empty_values
from utils.utils import build_command_string
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread

LIMIT = "result_limit"
LIMIT_ENABLE = "result_limit_enable"
OFFSET = "offset"
PROXY = "proxy"
SHODAN = "shodan"
SCREENSHOT = "screenshot"
DNS_RESOLUTION = "dns_resolution"
DNS_SERVER = "dns_server"
TAKEOVER_CHECK = "takeover_check"
SUBDOMAIN_RESOLUTION = "subdomain_resolution"
DNS_LOOKUP = "dns_lookup"
DNS_BRUTEFORCE = "dns_bruteforce"
SOURCE = "source"

TEMP_FILE_NAME = "tmp/the-harvester-temp"
SCREENSHOTS_DIRECTORY = "screenshots"

RUNNING_MESSAGE = "Running theHarvester with command: "
TOOL_DISPLAY_NAME = "theHarvester"
TOOL_NAME = "the_harvester"

NO_RESULTS_FOUND = "No results found."

scan_options = [
    ("Limit", "number", LIMIT, "For default value (500) leave empty"),
    ("Offset", "number", OFFSET, "For default value (0) leave empty"),
    ("Proxy", "text", PROXY, ""),
    ("Use Shodan", "checkbox", SHODAN, ""),
    ("Take Screenshots", "checkbox", SCREENSHOT, ""),
    ("Enable DNS Resolution", "checkbox", DNS_RESOLUTION, ""),
    ("DNS Server", "text", DNS_SERVER, ""),
    ("Perform Takeover Check", "checkbox", TAKEOVER_CHECK, ""),
    ("Perform Subdomain Resolution", "checkbox", SUBDOMAIN_RESOLUTION, ""),
    ("Enable DNS Lookup", "checkbox", DNS_LOOKUP, ""),
    ("Enable DNS Bruteforce", "checkbox", DNS_BRUTEFORCE, ""),
    (
        "Source",
        "select",
        SOURCE,
        [
            ("all", "All"),
            ("anubis", "Anubis"),
            ("baidu", "Baidu"),
            ("bevigil", "Bevigil"),
            ("binaryedge", "BinaryEdge"),
            ("bing", "Bing"),
            ("bingapi", "BingAPI"),
            ("bufferoverrun", "Bufferoverrun"),
            ("brave", "Brave"),
            ("censys", "Censys"),
            ("certspotter", "Certspotter"),
            ("criminalip", "Criminalip"),
            ("crtsh", "Crtsh"),
            ("dnsdumpster", "Dnsdumpster"),
            ("duckduckgo", "DuckDuckGo"),
            ("fullhunt", "Fullhunt"),
            ("github-code", "GitHub Code"),
            ("hackertarget", "Hackertarget"),
            ("hunter", "Hunter"),
            ("hunterhow", "Hunterhow"),
            ("intelx", "Intelx"),
            ("netlas", "Netlas"),
            ("onyphe", "Onyphe"),
            ("otx", "OTX"),
            ("projectDiscovery", "ProjectDiscovery"),
            ("rapiddns", "RapidDNS"),
            ("rocketreach", "Rocketreach"),
            ("securityTrails", "SecurityTrails"),
            ("sitedossier", "Sitedossier"),
            ("subdomaincenter", "Subdomaincenter"),
            ("subdomainfincerc99", "Subdomainfincerc99"),
            ("threatminer", "Threatminer"),
            ("tomba", "Tomba"),
            ("urlscan", "Urlscan"),
            ("vhost", "Vhost"),
            ("virustotal", "Virustotal"),
            ("yahoo", "Yahoo"),
            ("zoomeye", "Zoomeye"),
        ],
    ),
]


class TheHarvesterController(Controller):
    def __init__(self):
        super().__init__(TOOL_DISPLAY_NAME, TEMP_FILE_NAME, TOOL_NAME)

    def run(self, target: str, options: dict):
        self.screenshot_saved = False
        super().run(target, options)

    def __build_command__(self, target, options: dict):

        # check screenshot folder existance
        screenshot_folder = os.path.abspath(SCREENSHOTS_DIRECTORY)
        if not os.path.exists(screenshot_folder):
            os.makedirs(SCREENSHOTS_DIRECTORY)
        else:
            shutil.rmtree(SCREENSHOTS_DIRECTORY)
            os.makedirs(SCREENSHOTS_DIRECTORY)

        os.chmod(SCREENSHOTS_DIRECTORY, 0o777)

        # build command
        command = ["theHarvester", "-d", target, "-f", TEMP_FILE_NAME]

        if options.get(SOURCE, False):
            command.append("-b")
            command.append(options.get(SOURCE))
        else:
            command.append("-b")
            command.append("all")

        if options.get(LIMIT, False):
            command.append("-l")
            command.append(options.get(LIMIT))

        if options.get(OFFSET, False):
            command.append("-S")
            command.append(options.get(OFFSET))

        if options.get(PROXY, False):
            command.append("-p")
            command.append(options.get(PROXY))

        if options.get(SHODAN, False):
            command.append("-s")
            command.append(options.get(SHODAN))

        if options.get(SCREENSHOT, False):
            command.append("--screenshot")
            command.append(SCREENSHOTS_DIRECTORY)
            self.screenshot_saved = True

        if options.get(DNS_SERVER, False):
            command.append("-e")
            command.append(options.get(DNS_SERVER))

        if options.get(TAKEOVER_CHECK, False):
            command.append("-t")

        if options.get(DNS_RESOLUTION, False):
            command.append("-v")

        if options.get(DNS_LOOKUP, False):
            command.append("-n")

        if options.get(DNS_BRUTEFORCE, False):
            command.append("-c")

        if options.get(SUBDOMAIN_RESOLUTION, False):
            command.append("-r")

        return command

    def __run_command__(self, command):
        class TheHarvesterCommandThread(CommandThread):
            def run(self):
                super().run()
                print("\033[0m")
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__()

        return TheHarvesterCommandThread(command, self)

    def __remove_temp_file__(self):
        try:
            l.info(f"Removing temp {self.tool_display_name} files...")
            os.remove(self.temp_file_name + ".json")
            os.remove(self.temp_file_name + ".xml")
            l.success("Files removed successfully.")
        except Exception as e:
            l.error(f"Couldn't remove temp {self.tool_display_name} files.")
            print(e)

    def __parse_temp_results_file__(self):
        with open(TEMP_FILE_NAME + ".json", "r") as file:
            try:
                data = json.load(file)

                # check if screenshots are available
                if self.screenshot_saved:
                    data["screenshots_available"] = True
                else:
                    data["screenshots_available"] = False
            except Exception as e:
                return None, e

            return data, None

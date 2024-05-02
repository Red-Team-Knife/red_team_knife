import os, json
from utils.commands import build_command_string
from utils.html_format_util import *
from controllers.controller_thread import Controller, CommandThread
from loguru import logger as l

BURP = "burp"
BURP_REPLAY = "burp-replay"
SMART = "smart"
THOROUGH = "thorough"
PROXY = "proxy"
REPLAY_PROXY = "replay_proxy"
REPLAY_CODE = "replay_code"
USER_AGENT = "user_agent"
RANDOM_USER_AGENT = "random_user_agent"
EXTENSIONS = "extensions"
METHODS = "methods"
DATA = "data"
HEADERS = "headers"
COOKIES = "cookies"
QUERIES = "queries"
SLASH = "slash"
DONT_SCAN_URLS = "dont_scan_urls"
FILTER_MAX_DIMENSIONS = "filter_max_dimensions"
FILTER_REGEXES = "filter_regexes"
FILTER_WORD_NUMBERS = "filter_word_numbers"
FILTER_LINE_NUMBERS = "filter_line_numbers"
FILTER_STATUS_CODES = "filter_status_codes"
ALLOW_STATUS_CODES = "allow_status_codes"
REQUEST_TIMEOUT = "request_timeout"
AUTOMATIC_REDIRECT = "automatic_redirect"
INESCURE_DISABLE_TLS_CERTIFICATES = "insecure_disable_tls_certificates"
SERVER_CERTIFICATES = "server_certificates"
CLIENT_CERTIFICATE = "client_certificate"
CLIENT_KEY = "client_key"
THREADS = "threads"
DISABLE_RECURSION = "disable_recursion"
RECURSION_DEPTH = "recursion_depth"
FORCE_RECURSION = "force_recursion"
DONT_EXTRACT_LINKS = "dont_extract_links"
CONCURRENT_SCAN_LIMIT = "concurrent_scan_limit"
RATE_LIMIT = "rate_limit"
TIME_LIMIT = "time_limit"
WORDLIST_PATH = "wordlist_path"
AUTO_TUNE = "auto_tune"
AUTO_BAIL = "auto_bail"
DISABLE_WILDCARD_FILTERING = "disable_wildcard_filtering"
REMEMBER_EXTENSION = "remember_extension"
ASK_FOR_ALTERNATIVE_EXTENSIONS = "ask_for_alternative_extensions"
ADD_CRITICAL_WORDS = "add_critical_words"
IGNORE_EXTENSIONS = "ignore_extensions"

TEMP_FILE_NAME = "tmp/feroxbuster-temp"
TOOL_NAME = "Feroxbuster"
RUNNING_MESSAGE = f"Running {TOOL_NAME} with command: "


scan_options = [
    ("Set Burp", "checkbox", BURP, ""),
    ("Set Burp for Replay", "checkbox", BURP_REPLAY, ""),
    ("Set Smart Scan", "checkbox", SMART, ""),
    ("Set Smart Extension", "checkbox", THOROUGH, ""),
    ("Proxy", "text", PROXY, "http(s)://host:port"),
    ("Replay Proxy", "text", REPLAY_PROXY, "http(s)://host:port"),
    ("Replay Code", "number", REPLAY_CODE, "301"),
    ("User Agent", "text", USER_AGENT, "feroxbuster/2.10.1"),
    ("Set Random User Agent", "checkbox", RANDOM_USER_AGENT, ""),
    ("Extensions", "text", EXTENSIONS, "@ext.txt"),
    ("Methods", "text", METHODS, "GET"),
    ("Data", "text", DATA, "@post.bin"),
    ("Headers", "text", HEADERS, "Header:val"),
    ("Cookies", "text", COOKIES, "stuff=things"),
    ("Queries", "text", QUERIES, "token=stuff, secret=key"),
    ("Append Slash", "checkbox", SLASH, ""),
    ("Exclude from Recursion", "text", DONT_SCAN_URLS, "regex, urls"),
    ("Exclude Size", "number", FILTER_MAX_DIMENSIONS, "5120"),
    ("Filter Regexes", "text", FILTER_REGEXES, "'^ignore me$'"),
    ("Filter Word Number", "number", FILTER_WORD_NUMBERS, "312"),
    ("Filter Line Number", "number", FILTER_LINE_NUMBERS, "20"),
    ("Filter Out Status Codes", "number", FILTER_STATUS_CODES, "404"),
    ("Filter In Status Codes", "number", ALLOW_STATUS_CODES, "All Included"),
    ("Request Timeout", "number", REQUEST_TIMEOUT, "7"),
    ("Allow Automatic Redirect", "checkbox", AUTOMATIC_REDIRECT, ""),
    (
        "Allow Insecure TLS Certificates",
        "checkbox",
        INESCURE_DISABLE_TLS_CERTIFICATES,
        "",
    ),
    ("Add PEM Server Certificates", "text", SERVER_CERTIFICATES, ""),
    ("Add PEM Client Certificates", "text", CLIENT_CERTIFICATE, ""),
    ("Add PEM Client Key", "text", CLIENT_KEY, ""),
    ("Threads", "number", THREADS, "50"),
    ("Disable Recursion", "checkbox", DISABLE_RECURSION, ""),
    ("Recursion Depth", "number", RECURSION_DEPTH, "4"),
    ("Enable Force Recursion", "checkbox", FORCE_RECURSION, ""),
    ("Disable Link Extraction", "checkbox", DONT_EXTRACT_LINKS, ""),
    ("Concurrent Scan Limit", "number", CONCURRENT_SCAN_LIMIT, "0"),
    ("Set Limit Number of Request", "number", RATE_LIMIT, "0"),
    ("Wordlist", "text", WORDLIST_PATH, "Path or URL"),
    ("Enable Auto Tune", "checkbox", AUTO_TUNE, ""),
    ("Enable Auto Bail", "checkbox", AUTO_BAIL, ""),
    ("Disable Wildcard Filtering", "checkbox", DISABLE_WILDCARD_FILTERING, ""),
    ("Scan Time Limit", "text", TIME_LIMIT, "5s, 10m, 3h..."),
    ("Enable Extension Autocollecting", "checkbox", REMEMBER_EXTENSION, ""),
    (
        "Enable Request for Alternative Extensions",
        "checkbox",
        ASK_FOR_ALTERNATIVE_EXTENSIONS,
        "",
    ),
    ("Enable Critical Words Autocollecting", "checkbox", ADD_CRITICAL_WORDS, ""),
    ("Ignore Extensions", "text", IGNORE_EXTENSIONS, ""),
]


class FeroxbusterController(Controller):

    def __init__(self):
        super().__init__()
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.tool_name = TOOL_NAME

    def run(self, target, options: dict):
        self.last_scan_result = None

        command = [
            "feroxbuster",
            "-u",
            target,
            "-o",
            TEMP_FILE_NAME,
            "--json",
            "--no-state",
        ]

        # composite settings
        if options.get(BURP, False):
            command.append("--burp")
        if options.get(BURP_REPLAY, False):
            command.append("--burp-replay")
        if options.get(SMART, False):
            command.append("--smart")
        if options.get(THOROUGH, False):
            command.append("--thorough")

        # proxy settings
        if options.get(PROXY, False):
            command.append("--proxy")
            command.append(options[PROXY])
        if options.get(REPLAY_PROXY, False):
            command.append("--replay-proxy")
            command.append(options[REPLAY_PROXY])
        if options.get(REPLAY_CODE, False):  # TODO it's a list
            command.append("--replay-codes")
            command.append(options[REPLAY_CODE])

        # requests settings

        if options.get(USER_AGENT, False):
            command.append("-a")
            command.append(options[USER_AGENT])
        if options.get(RANDOM_USER_AGENT, False):
            command.append("-A")
        if options.get(EXTENSIONS, False):
            for i in options[EXTENSIONS]:
                command.append("-x")
                command.append(i)
        if options.get(METHODS, False):
            for i in options[METHODS]:
                command.append("-m")
                command.append(i)
        if options.get(DATA, False):
            command.append("--data")
            command.append(options[DATA])
        if options.get(HEADERS, False):
            for i in options[HEADERS]:
                command.append("-H")
                command.append(i)
        if options.get(COOKIES, False):
            for i in options[COOKIES]:
                command.append("-b")
                command.append(i)
        if options.get(QUERIES, False):
            for i in options[QUERIES]:
                command.append("-Q")
                command.append(i)
        if options.get(SLASH, False):
            command.append("-f")

        # request filters

        if options.get(DONT_SCAN_URLS, False):
            command.append("--dont-scan")
            for i in options[DONT_SCAN_URLS]:
                command.append(i)

        # response filters

        if options.get(FILTER_MAX_DIMENSIONS, False):
            for i in options[FILTER_MAX_DIMENSIONS]:
                command.append("-S")
                command.append(i)
        if options.get(FILTER_REGEXES, False):
            for i in options[FILTER_REGEXES]:
                command.append("-X")
                command.append(i)
        if options.get(FILTER_WORD_NUMBERS, False):
            for i in options[FILTER_WORD_NUMBERS]:
                command.append("-W")
                command.append(i)
        if options.get(FILTER_LINE_NUMBERS, False):
            for i in options[FILTER_LINE_NUMBERS]:
                command.append("-N")
                command.append(i)
        if options.get(FILTER_STATUS_CODES, False):
            for i in options[FILTER_STATUS_CODES]:
                command.append("-C")
                command.append(i)
        if options.get(ALLOW_STATUS_CODES, False):
            for i in options[ALLOW_STATUS_CODES]:
                command.append("-s")
                command.append(i)

        # client options
        if options.get(REQUEST_TIMEOUT, False):
            command.append("-T")
            command.append(options[REQUEST_TIMEOUT])

        if options.get(AUTOMATIC_REDIRECT, False):
            command.append("-r")
        if options.get(INESCURE_DISABLE_TLS_CERTIFICATES, False):
            command.append("-k")
        if options.get(SERVER_CERTIFICATES, False):
            command.append("--server-certs")
            for i in options[SERVER_CERTIFICATES]:
                command.append(i)
        if options.get(CLIENT_CERTIFICATE, False):
            command.append("--client-cert")
            command.append(options[CLIENT_CERTIFICATE])
        if options.get(CLIENT_KEY, False):
            command.append("--client-key")
            command.append(options[CLIENT_KEY])

        # scan options
        if options.get(THREADS, False):
            command.append("-t")
            command.append(options[THREADS])
        if options.get(DISABLE_RECURSION, False):
            command.append("-n")
        if options.get(RECURSION_DEPTH, False):
            command.append("-d")
            command.append(options[RECURSION_DEPTH])
        if options.get(FORCE_RECURSION, False):
            command.append("--force-recursion")
        if options.get(DONT_EXTRACT_LINKS, False):
            command.append("--dont-extract-links")
        if options.get(CONCURRENT_SCAN_LIMIT, False):
            command.append("-L")
            command.append(options[CONCURRENT_SCAN_LIMIT])
        if options.get(RATE_LIMIT, False):
            command.append("--rate-limit")
            command.append(options[RATE_LIMIT])
        if options.get(TIME_LIMIT, False):
            command.append("--time-limit")
            command.append(options[TIME_LIMIT])
        if options.get(WORDLIST_PATH, False):
            command.append("--time-limit")
            command.append(options[WORDLIST_PATH])
        if options.get(AUTO_TUNE, False):
            command.append("--auto-tune")
        if options.get(AUTO_BAIL, False):
            command.append("--auto-bail")
        if options.get(DISABLE_WILDCARD_FILTERING, False):
            command.append("-D")

        # dynamic collection settings
        if options.get(REMEMBER_EXTENSION, False):
            command.append("-E")
            if options.get(IGNORE_EXTENSIONS, False):
                for i in options[IGNORE_EXTENSIONS]:
                    command.append("-I")
                    command.append(i)
        if options.get(ASK_FOR_ALTERNATIVE_EXTENSIONS, False):
            command.append("-B")
        if options.get(ADD_CRITICAL_WORDS, False):
            command.append("-g")

        self.__log_running_message__(command)

        class FeroxbusterCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__(TEMP_FILE_NAME)

            def stop(self):
                super().stop()
                self.print_stop_completed_message()

        self.thread = FeroxbusterCommandThread(command, self)
        self.thread.start()

    # TODO metodo generale __format_result__ con
    # def ...
    #      l.info inizio
    #      formattazione vera
    #       l.info fine
    def __format_result__(self):

        if not self.last_scan_result:
            # List to store parsed JSON objects
            json_objects = []

            # Read the file line by line and parse JSON
            with open(TEMP_FILE_NAME, "r") as file:
                l.info(f"Parsing {self.tool_name} temp file...")
                for line in file:
                    try:

                        # Parse the JSON from the line
                        json_object = json.loads(line.strip())
                        # Append the parsed JSON object to the list
                        json_objects.append(json_object)
                        l.success("File parsed successfully.")
                    except json.JSONDecodeError as e:
                        l.error("Error parsing temp JSON file.")
                        print(e)

            self.__remove_temp_file__(TEMP_FILE_NAME)

            self.last_scan_result = json_objects

        l.info(f"Generating html for {self.tool_name} results...")
        # Create a dict with the following structure:
        # { code1 : [resource1, resource2, ...],
        #   code2: [resource11, resource12, ...]}
        sorted = {}
        for i in self.last_scan_result:
            if i.get("status", False):
                status = i["status"]
                if sorted.get(status, False):
                    sorted[status].append(i)
                else:
                    sorted[status] = [i]

        # Extract status codes and build a string
        status_codes = ""
        for code in list(sorted.keys()):
            status_codes += str(code)
            status_codes += ", "

        status_codes = status_codes[:-2]

        html_output = f"""
        <h1>Status codes: {status_codes}</h1>
                        <table>
                        """

        for key in list(sorted.keys()):
            html_output += f"""
                <tr>
                    <td style="font-size: 24px;"><b>{key}</b></td>
                </tr>
                """

            items = ""
            for i in sorted[key]:
                items += "<tr><td><table>"
                items += render_dictionary_as_table(i)
                items += "</table></td></tr>"

            html_output += items
        html_output += "</table>"
        l.success("Html generated successfully.")
        return html_output

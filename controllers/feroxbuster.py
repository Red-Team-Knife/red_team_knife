import subprocess, os, json, shutil
from utils.html_format_util import *

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
PARALLEL_INSTANCES = "parallel_instances"
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

TEMP_FILE_NAME = "feroxbuster-temp"


class FeroxbusterController:
    def __init__(self):
        self.scan_result = None

    def run(self, target, options: dict):
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
        if options.get(PARALLEL_INSTANCES, False):
            command.append("--parallel")
            command.append(options[PARALLEL_INSTANCES])
        if options.get(RATE_LIMIT, False):
            command.append("--rate_limit")
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

        print(command)

        feroxbuster_process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        # Print output while the command is running
        while True:
            output = feroxbuster_process.stdout.readline()
            if output == "" and feroxbuster_process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Wait for the process to terminate
        feroxbuster_process.wait()

        return self.format_result()

    def format_result(self):

        # List to store parsed JSON objects
        json_objects = []

        # Read the file line by line and parse JSON
        with open(TEMP_FILE_NAME, "r") as file:
            for line in file:
                try:
                    # Parse the JSON from the line
                    json_object = json.loads(line.strip())
                    # Append the parsed JSON object to the list
                    json_objects.append(json_object)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")

        sorted = {}
        for i in json_objects:
            status = i["status"]
            if sorted.get(status, False):
                sorted[status].append(i)
            else:
                sorted[status] = [i]

        status_codes = ''
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
                items += "<tr><td>"
                items += render_dictionary(i)
                items += "</td></tr>"

            html_output += items
        html_output += "</table>"
        return html_output

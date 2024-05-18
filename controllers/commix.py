import pathlib, os
import shutil
from threading import Thread
from typing import Tuple
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread
from loguru import logger as l


SET_CRAWL_DEPTH = "set_crawl_depth"
SET_REGEX_EXCLUSION = "set_regex_exclusion"
SET_HTTP_METHOD = "set_http_method"
SET_DATA = "set_data"
SET_HOST_HEADER = "set_host_header"
SET_REFERER_HEADER = "set_referer_header"
SET_USER_AGENT_HEADER = "set_user_agent_header"
SET_SPLIT_CHAR = "set_split_char"
SET_COOKIE = "set_cookie"
SET_SPLIT_COOKIE = "set_split_cookie"
SET_EXTRA_HEADER = "set_extra_header"
SET_PROXY = "set_proxy"
SET_TOR = "set_tor"
SET_TOR_PORT = "set_tor_port"
CHECK_TOR = "check_tor"
SET_AUTH_TYPE = "set_auth_type"
SET_AUTH_CREDS = "set_auth_creds"
SET_AUTH_URL = "set_auth_url"
SET_AUTH_DATA = "set_auth_data"
SET_IGNORE_CODE = "set_ignore_code"
FORCE_SSL = "force_ssl"
IGNORE_PROXY = "ignore_proxy"
IGNORE_REDIRECTS = "ignore_redirects"
SET_TIMEOUT = "set_timeout"
SET_RETRIES = "set_retries"
DROP_SET_COOKIE = "drop_set_cookie"
RETRIEVE_ALL = "retrieve_all"
RETRIEVE_CURRENT_USER = "retrieve_current_user"
RETRIEVE_HOSTNAME = "retrieve_hostname"
CHECK_USER_ROOT = "check_user_root"
CHECK_USER_ADMIN = "check_user_admin"
RETRIEVE_INFO = "retrieve_info"
RETRIEVE_USERS = "retrieve_users"
RETRIEVE_PASSWORD_HASH = "retrieve_password_hash"
LIST_PRIVILEGES = "list_privileges"
PS_VERSION = "ps_version"
READ_FILE = "read_file"
WRITE_FILE = "write_file"
UPLOAD_FILE = "upload_file"
FILE_DEST = "file_dest"
SET_SHELLSHOCK = "set_shellshock"
SET_PARAMETER = "set_parameter"
SKIP_PARAMETERS = "skip_parameters"
SET_SUFFIX = "set_suffix"
SET_PREFIX = "set_prefix"
SET_TECHNIQUE = "set_technique"
SKIP_TECHNIQUE = "skip_technique"
MAX_LEN = "max_len"
SET_DELAY = "set_delay"
SET_WEB_ROOT = "set_web_root"
SET_TAMPER = "set_tamper"
SET_LEVEL = "set_level"
SKIP_MATH = "skip_math"
SKIP_EMPTY = "skip_empty"
SET_TRIES = "set_tries"
SET_HEURISTIC = "set_heuristic"
FORCE_OS = "force_os"
OS_SHELL = "os_shell"
EXECUTE_COMMAND = "execute_command"
ALTER_SHELL = "alter_shell"
RADIO_SHELLS = "radio_shells"

OS_SHELL_MSG = 'You can try to spawn an OS Shell via commix by running this command in a terminal (you have to put data in <> tags):'
OS_SHELL_COMMAND= 'commix -u {} --data {} --batch'
ALTER_SHELL_MSG = 'You can try to spawn an OS Shell via commix by running this command in a terminal (you have to put data in <> tags):'
ALTER_SHELL_COMMAND = 'commix -u {} --data {} --alter-shell <Es. Python> --batch'
EXECUTE_CMD_MSG = 'You can try to execute a command via commix by running this command in a terminal (you have to put data in <> tags):'
EXECUTE_CMD_COMMAND = 'sqlmap -u {} --data {} --batch --os-cmd <command>'

TOOL_DISPLAY_NAME = "Commix"
TOOL_NAME = "commix"
RUNNING_MESSAGE = f"Running {TOOL_DISPLAY_NAME} with command: "
TEMP_FILE_NAME = "tmp/commix-temp"



scan_option = [
    ("Spawn an OS Shell", "radio", OS_SHELL, RADIO_SHELLS),
    ("Execute a Command", "radio", EXECUTE_COMMAND, RADIO_SHELLS),
    ("Use an Alternative Shell", "radio", ALTER_SHELL, RADIO_SHELLS),
    ("Set Crawl Depth", "number", SET_CRAWL_DEPTH, "Default 1"),
    ("Set Regex to exclude from Crawl", "text", SET_REGEX_EXCLUSION, ""),
    ("Set an HTTP method to be used forcibly", "text", SET_HTTP_METHOD, "PUT, GET ..."),
    ("Set Data", "text", SET_DATA, "id=* / data1=*&data2=*"),
    ("Set HTTP Host Header", "text", SET_HOST_HEADER, ""),
    ("Set HTTP Referer Header", "text", SET_REFERER_HEADER, ""),
    ("Set HTTP User-Agent Header", "text", SET_USER_AGENT_HEADER, ""),
    ("Set a Char to Use as Parameter Split", "text", SET_SPLIT_CHAR, ""),
    ("Set Cookie", "text", SET_COOKIE, ""),
    ("Set a Char to split Cookie Values", "text", SET_SPLIT_COOKIE, ""),
    ("Set Extra Header", "text", SET_EXTRA_HEADER, ""),
    ("Set Proxy to connect with", "text", SET_PROXY, "http://proxy.com"),
    ("Set Tor", "checkbox", SET_TOR, ""),
    ("Set Tor Port", "number", SET_TOR_PORT, "Default 8118"),
    ("Check for Tor Usage", "checkbox", CHECK_TOR, ""),
    ("Set Authentication Type", "text", SET_AUTH_TYPE, "Basic, Digest, Bearer"),
    ("Set Authentication Credentials", "text", SET_AUTH_CREDS, "name:password"),
    ("Set Authentication Url", "text", SET_AUTH_URL, ""),
    ("Set Authentication Data", "text", SET_AUTH_DATA, ""),
    ("Set HTTP Code to Ignore", "number", SET_IGNORE_CODE, "404, 301"),
    ("Force SSL", "checkbox", FORCE_SSL, ""),
    ("Ignore Proxy", "checkbox", IGNORE_PROXY, ""),
    ("Ignore Redirects", "checkbox", IGNORE_REDIRECTS, ""),
    ("Set Timeout", "number", SET_TIMEOUT, "Default 30"),
    ("Set Connection Retries", "number", SET_RETRIES, "Default 3"),
    ("Ignore Set-Cookie Header from Response", "checkbox", DROP_SET_COOKIE, ""),
    ("Retrieve Everything", "checkbox", RETRIEVE_ALL, ""),
    ("Retrieve current User", "checkbox", RETRIEVE_CURRENT_USER, ""),
    ("Retrieve Hostname", "checkbox", RETRIEVE_HOSTNAME, ""),
    ("Check if Current User is Root", "checkbox", CHECK_USER_ROOT, ""),
    ("Check if Current User is Admin", "checkbox", CHECK_USER_ADMIN, ""),
    ("Retrieve System Info", "checkbox", RETRIEVE_INFO, ""),
    ("Retrieve System Users", "checkbox", RETRIEVE_USERS, ""),
    ("Retrieve Password Hashes", "checkbox", RETRIEVE_PASSWORD_HASH, ""),
    ("List Priviledges", "checkbox", LIST_PRIVILEGES, ""),    
    ("Retrieve PowerShell's Version", "checkbox", PS_VERSION, ""),
    ("Read a File", "text", READ_FILE, ""),
    ("Write to a File", "text", WRITE_FILE, ""),
    ("Upload a File", "text", UPLOAD_FILE, ""),
    ("Set Host's absolute filepath to write and/or upload to", "text", FILE_DEST, ""),
    ("Set Shellshock Injection Module", "checkbox", SET_SHELLSHOCK, ""),
    ("Set a Parameter to Test", "text", SET_PARAMETER, "id"),
    ("Set Parameters to Skip", "text", SKIP_PARAMETERS, "id"),
    ("Set Injection suffix", "text", SET_SUFFIX, ""),
    ("Set Injection prefix", "text", SET_PREFIX, ""),
    ("Specify Injection technique", "text", SET_TECHNIQUE, ""),
    ("Specify Injection technique to Skip", "text", SKIP_TECHNIQUE, ""),
    ("Specify Max length for Time Injections", "number", MAX_LEN, "Default 10000"),
    ("Set Requests Delay", "number", SET_DELAY, ""),
    ("Set Web Server Root Directory", "text", SET_WEB_ROOT, ""),
    ("Set Os target", "text", FORCE_OS, "Unix, Windows"),
    ("Set Tamper", "text", SET_TAMPER, ""),
    ("Set Tests Level", "number", SET_LEVEL, "1-3"),
    ("Skip Mathematic in Detection Phase", "checkbox", SKIP_MATH, ""),
    ("Skip Testing Empty-Value Parameters", "checkbox", SKIP_EMPTY, ""),
    ("Set Tries for File-based Technique", "checkbox", SET_TRIES, ""),
    ("Perform only Positive Heuristic Tests", "checkbox", SET_HEURISTIC, ""),
]



class CommixController(Controller):
    
    def __init__(self):
        super().__init__(TOOL_NAME, TOOL_DISPLAY_NAME)
        self.os_shell = False
        self.shell_option = None
        self.target = None
        self.data = None
        
        
    def __build_command__(self, target: str, options: dict) -> list:
        
        self.os_shell = False
        self.shell_option = None
        self.target = None
        self.data = None
        temp_path = os.path.join(os.getcwd(), TEMP_FILE_NAME)
        
        # Create tmp Folder
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        
        command = [
            "commix",
            "-u",
            target,
            "--output-dir",
            temp_path,
            "-v", 
            "2",
            '--answers', 
            "Do you want to prompt for a pseudo-terminal shell?=N",
            "--batch",
        ]
        
        self.target = target
        
        if options.get(RADIO_SHELLS, False):
            self.os_shell = True
            self.shell_option = options[RADIO_SHELLS]
            self.target = target
        
        if options.get(SET_CRAWL_DEPTH, False):
            command.extend(["--crawl", options[SET_CRAWL_DEPTH]])

        if options.get(SET_REGEX_EXCLUSION, False):
            command.extend(["--crawl-exclude=", options[SET_REGEX_EXCLUSION]])

        if options.get(SET_HTTP_METHOD, False):
            command.extend(["--method=", f"{options[SET_HTTP_METHOD]}"])

        if options.get(SET_DATA, False):
            self.data = options[SET_DATA]
            command.extend(["--data=", self.data])

        if options.get(SET_HOST_HEADER, False):
            command.extend(["--host=", f"{options[SET_HOST_HEADER]}"])

        if options.get(SET_REFERER_HEADER, False):
            command.extend(["--referer=", f"{options[SET_REFERER_HEADER]}"])

        if options.get(SET_USER_AGENT_HEADER, False):
            command.extend(["--user-agent=", f"{options[SET_USER_AGENT_HEADER]}"])

        if options.get(SET_SPLIT_CHAR, False):
            command.extend(["--param-del=", f"{options[SET_SPLIT_CHAR]}"])

        if options.get(SET_COOKIE, False):
            command.extend(["--cookie=", f"{options[SET_COOKIE]}"])

        if options.get(SET_SPLIT_COOKIE, False):
            command.extend(["--cookie-del=", f"{options[SET_SPLIT_COOKIE]}"])

        if options.get(SET_EXTRA_HEADER, False):
            command.extend(["-H", f"{options[SET_EXTRA_HEADER]}"])

        if options.get(SET_PROXY, False):
            command.extend(["--proxy=", f"{options[SET_PROXY]}"])

        if options.get(SET_TOR, False):
            command.append("--tor")

        if options.get(SET_TOR_PORT, False):
            command.extend(["--tor-port=", options[SET_TOR_PORT]])

        if options.get(CHECK_TOR, False):
            command.append("--tor-check")

        if options.get(SET_AUTH_TYPE, False):
            command.extend(["--auth-type=", f"{options[SET_AUTH_TYPE]}"])
            
        if options.get(SET_AUTH_CREDS, False):
            command.extend(["--auth-cred=", f"{options[SET_AUTH_CREDS]}"])

        if options.get(SET_AUTH_URL, False):
            command.extend(["--auth-url=", f"{options[SET_AUTH_URL]}"])

        if options.get(SET_AUTH_DATA, False):
            command.extend(["--auth-data=", f"{options[SET_AUTH_DATA]}"])

        if options.get(SET_IGNORE_CODE, False):
            command.extend(["--ignore-code=", f"{options[SET_IGNORE_CODE]}"])

        if options.get(FORCE_SSL, False):
            command.append("--force-ssl")

        if options.get(IGNORE_PROXY, False):
            command.append("--ignore-proxy")

        if options.get(IGNORE_REDIRECTS, False):
            command.append("--ignore-redirects")

        if options.get(SET_TIMEOUT, False):
            command.extend(["--timeout=", options[SET_TIMEOUT]])

        if options.get(SET_RETRIES, False):
            command.extend(["--retries=", options[SET_RETRIES]])

        if options.get(DROP_SET_COOKIE, False):
            command.append("--drop-set-cookie")

        if options.get(RETRIEVE_ALL, False):
            command.append("--all")

        if options.get(RETRIEVE_CURRENT_USER, False):
            command.append("--current-user")

        if options.get(RETRIEVE_HOSTNAME, False):
            command.append("--hostname")

        if options.get(CHECK_USER_ROOT, False):
            command.append("--is-root")

        if options.get(CHECK_USER_ADMIN, False):
            command.append("--is-admin")

        if options.get(RETRIEVE_INFO, False):
            command.append("--sys-info")

        if options.get(RETRIEVE_USERS, False):
            command.append("--users")

        if options.get(RETRIEVE_PASSWORD_HASH, False):
            command.append("--passwords")

        if options.get(LIST_PRIVILEGES, False):
            command.append("--privileges")

        if options.get(PS_VERSION, False):
            command.append("--ps-version")

        if options.get(READ_FILE, False):
            command.extend(["--file-read=", f"{options[READ_FILE]}"])

        if options.get(WRITE_FILE, False):
            command.extend(["--file-write=", f"{options[WRITE_FILE]}"])

        if options.get(UPLOAD_FILE, False):
            command.extend(["--file-upload=", f"{options[UPLOAD_FILE]}"])

        if options.get(FILE_DEST, False):
            command.extend(["--file-dest=", f"{options[FILE_DEST]}"])

        if options.get(SET_SHELLSHOCK, False):
            command.append("--shellshock")

        if options.get(SET_PARAMETER, False):
            command.extend(["-p", options[SET_IGNORE_CODE]])

        if options.get(SKIP_PARAMETERS, False):
            command.extend(["--skip=", f"{options[SKIP_PARAMETERS]}"])

        if options.get(SET_SUFFIX, False):
            command.extend(["--suffix=", f"{options[SET_SUFFIX]}"])

        if options.get(SET_PREFIX, False):
            command.extend(["--prefix=", f"{options[SET_PREFIX]}"])

        if options.get(SET_TECHNIQUE, False):
            command.extend(["--technique=", f"{options[SET_TECHNIQUE  ]}"])

        if options.get(SKIP_TECHNIQUE, False):
            command.extend(["--skip-technique=", f"{options[SKIP_TECHNIQUE]}"])

        if options.get(MAX_LEN, False):
            command.extend(["--maxlen=", f"{options[MAX_LEN]}"])

        if options.get(SET_DELAY, False):
            command.extend(["--delay=", f"{options[SET_DELAY]}"])

        if options.get(SET_WEB_ROOT, False):
            command.extend(["--web-root=", f"{options[SET_WEB_ROOT]}"])
            
        if options.get(FORCE_OS, False):
            command.extend(["--os=", options[FORCE_OS]])

        if options.get(SET_TAMPER, False):
            command.extend(["--tamper=", f"{options[SET_TAMPER]}"])

        if options.get(SET_LEVEL, False):
            command.extend(["--level", options[SET_LEVEL]])

        if options.get(SKIP_MATH, False):
            command.append("--skip-calc")

        if options.get(SKIP_EMPTY, False):
            command.append("--skip-empty")

        if options.get(SET_TRIES, False):
            command.extend(["--failed-tries=", options[SET_TRIES]])

        if options.get(SET_HEURISTIC, False):
            command.append("--smart")
        
        return command
    
    def __run_command__(self, command) -> Thread:
        class CommixCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__()
        return CommixCommandThread(command, self)
        
    def __remove_temp_file__(self):
        """
        Needs to override super method because commix saves temp files in more folders.
        Removes a temporary results folder
        """
        try:
            l.info(f"Removing temp {self.tool_name} folder...")
            shutil.rmtree(TEMP_FILE_NAME)
            l.success("File removed successfully.")
        except Exception as e:
            l.error(f"Couldn't remove temp {self.tool_name} folder.")
            print(e)
            
    def __parse_temp_results_file__(self) -> Tuple[object, Exception]:
        json_objects = ''
        
        TMP_PATH = "./" + TEMP_FILE_NAME
        
        for scan in os.listdir(TMP_PATH):
            scan_path = os.path.join(TMP_PATH, scan)
            
            if os.path.isdir(scan_path):
                with open(os.path.join(scan_path, "logs.txt"), "r") as file:
                    json_objects += file.read()
                                
        return json_objects, None
    
    def __format_html__(self) -> str:
        html_output = ""
    
        if self.os_shell:
            if self.shell_option == OS_SHELL:
                html_output += f'<p>{OS_SHELL_MSG}</p>'
                html_output += f'<textarea readonly style="width: calc(100%); height: 45px; font-family: \'Courier New\', Courier, monospace;"> '
                html_output += OS_SHELL_COMMAND.format(self.target, self.data)
            elif self.shell_option == ALTER_SHELL:
                html_output += f'<p>{ALTER_SHELL_MSG}</p>'
                html_output += f'<textarea readonly style="width: calc(100%); height: 45px; font-family: \'Courier New\', Courier, monospace;"> '
                html_output += ALTER_SHELL_COMMAND.format(self.target, self.data)
            elif self.shell_option == EXECUTE_COMMAND:
                html_output += f'<p>{EXECUTE_CMD_MSG}</p>'
                html_output += f'<textarea readonly style="width: calc(100%); height: 45px; font-family: \'Courier New\', Courier, monospace;"> '
                html_output += EXECUTE_CMD_MSG.format(self.target, self.data)                
                
            html_output += "</textarea><br><br>"
            
        
        html_output += "<textarea readonly class='exploit_textarea'>"
        html_output += self.last_scan_result
        html_output += " </textarea>"
        
        
        return html_output

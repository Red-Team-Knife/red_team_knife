import threading
import subprocess, os, json, shutil, time
import copy

from utils.utils import build_command_string
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread
from controllers.search_exploit import SearchExploitController
import xmltodict

PORT_RANGE = "port_range"

script_options = [
    ("Port Range", "text", PORT_RANGE, "22, 21-25"),
]

RUNNING_MESSAGE = "Running Nmap vulnerability scan with command: "
TOOL_DISPLAY_NAME = "Nmap-Vuln Scan"
TOOL_NAME = "nmap_vuln"
SCRIPT_PATH = "nmap-vulners/"
TEMP_FILE_NAME = "tmp/nmap-vuln-temp"

search_exploit_controller = SearchExploitController()


class NmapVulnController(Controller):
    def __init__(self):
        super().__init__(TOOL_DISPLAY_NAME, TEMP_FILE_NAME, TOOL_NAME)

    def __build_command__(self, target, options):
        command = [
            "nmap",
            "--script",
            SCRIPT_PATH,
            "-sV",
            "-oX",
            TEMP_FILE_NAME,
            target,
        ]
        if options.get(PORT_RANGE, False):
            command.extend(["-p", options[PORT_RANGE]])

        return command

    def __run_command__(self, command):
        class NmapCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__(TEMP_FILE_NAME)

        return NmapCommandThread(command, self)

    def __parse_temp_results_file__(self):
        with open(TEMP_FILE_NAME, "r") as file:
            try:
                xml_dict = xmltodict.parse(file.read())

                json_string = json.dumps(xml_dict)

                json_objects = json.loads(json_string)
                if (json_objects["nmaprun"]["host"]["ports"].get("port")):
                    json_objects = json_objects["nmaprun"]["host"]["ports"]["port"]
                else:
                    json_objects = {}
                
            except Exception as e:
                return None, e
        return json_objects, None

import threading
import subprocess, os, json, shutil, time

from utils.commands import build_command_string
from controllers.controller_thread import Controller, CommandThread
import xmltodict

script_options = []
RUNNING_MESSAGE = "Running Nmap vulnerability scan with command: "
TOOL_NAME = "Nmap-Vuln Scan"
SCRIPT_PATH= "nmap-vulners/"
TEMP_FILE_NAME = "tmp/nmap_vuln-temp"


class NmapVulnController(Controller):
    def __init__(self):
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.tool_name = TOOL_NAME

    def run(self, target, options):
        self.last_scan_result = None

        command = [
            "nmap",
            "--script",
            SCRIPT_PATH,
            "-sV",
            "-oX",
            TEMP_FILE_NAME,
            target
        ]

        command_string = build_command_string(command)

        print(RUNNING_MESSAGE + command_string[:-1]) 

        class NmapCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    try:
                        os.remove(TEMP_FILE_NAME)
                    except:
                        print("Couldn't remove temp Nmap file.")
        self.thread = NmapCommandThread(command, self)
        self.thread.start()

    def __format_result__(self):
        if not self.last_scan_result:

            with open(TEMP_FILE_NAME, "r") as file:

                xml_dict = xmltodict.parse(file.read())

                json_string = json.dumps(xml_dict)

                json_objects = json.loads(json_string)
                json_objects = json_objects["nmaprun"]["host"]["ports"]["port"]
            
            os.remove(TEMP_FILE_NAME)

            with open("test.json", "w") as file:
                print(json.dumps(json_objects), file=file)

            self.last_scan_result = json_objects

        return f'<p>{self.last_scan_result}</p>'


    def __format_html__(self):
        html_string = ''

        # build port details table
        for port_table in self.last_scan_result:
            html_string += '<table>'
            html_string += '<tr>'
            port_table.pop("script")

            # build table headers
            for header in port_table.keys():
                html_string += '<th>{}</th>'.format(header.replace("@", ""))
            html_string += '</tr>\n'

            # add rows
            for row in port_table:
                html_string += '<tr>'

            


        


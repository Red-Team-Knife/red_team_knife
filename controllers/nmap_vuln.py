import threading
import subprocess, os, json, shutil, time
import copy

from utils.commands import build_command_string
from controllers.controller_thread import Controller, CommandThread
from controllers.search_exploit import SearchExploitController
import xmltodict

script_options = []
RUNNING_MESSAGE = "Running Nmap vulnerability scan with command: "
TOOL_NAME = "Nmap-Vuln Scan"
SCRIPT_PATH = "nmap-vulners/"
TEMP_FILE_NAME = "tmp/nmap-vuln-temp"

search_exploit_controller = SearchExploitController()


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
            target,
        ]

        self.__log_running_message__(command)

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

            self.last_scan_result = json_objects

        return self.__format_html__()

    def __format_html__(self):

        last_scan_result = copy.deepcopy(self.last_scan_result)

        html_string = ""
        # build port details table
        for port_table in last_scan_result:
            html_string += "<b>Port:</b>"
            html_string += "<table>"
            html_string += "<tr>"

            if port_table.get("script", False):
                script_table = port_table.pop("script")

            # build table headers
            for header in port_table:
                html_string += "<th>{}</th>".format(header.replace("@", ""))
            html_string += "</tr>\n"

            # add rows
            html_string += "<tr>"
            for row in port_table:
                if isinstance(port_table[row], dict):
                    html_string += "<td>"
                    # fill field with subdictionary values
                    for subkey in port_table[row]:
                        html_string += f'<b>{subkey.replace("@", "")}: </b>'

                        if type(port_table[row][subkey]) is list:
                            html_string += f"{ ', '.join(port_table[row][subkey])} <br>"
                        else:
                            html_string += f"{port_table[row][subkey]} <br>"
                    html_string += "</td>"
                else:
                    html_string += "<td>{}</td>".format(port_table[row])
            html_string += "</tr>\n"
            html_string += "</table><br>\n"

            # build cve table
            if script_table:
                # initializing table
                if type(script_table) is list:
                    filtered_list = []

                    for element in script_table:
                        if element.get("table", False):
                            filtered_list.append(element)
                    html_string += "<b>Vulns:</b>"
                    html_string += '<table class="vuln_table">'
                    html_string += "<tr>"

                    cve_table = filtered_list[0]["table"]
                    cve_table = cve_table.get("table")

                elif not script_table.get("table"):
                    html_string += "<b>No Vulns Found</b><br><br>"
                    break

                else:
                    html_string += "<b>Vulns:</b>"
                    html_string += '<table class="vuln_table">'
                    html_string += "<tr>"
                    cve_table = script_table["table"]
                    cve_table = cve_table.get("table")

                # sort vuln list for "is_exploit" attr
                cve_table = sorted(
                    cve_table,
                    key=lambda x: (
                        0
                        if next(
                            item["#text"]
                            for item in x["elem"]
                            if item["@key"] == "is_exploit"
                        )
                        == "true"
                        else 1
                    ),
                )

                # reorder dictionaries
                cve_table = [
                    {
                        "elem": sorted(
                            item["elem"],
                            key=lambda x: ["id", "type", "is_exploit", "cvss"].index(
                                x["@key"]
                            ),
                        )
                    }
                    for item in cve_table
                ]

                # build headers
                for header in cve_table[0]["elem"]:
                    html_string += "<th>{}</th>".format(header["@key"].replace("@", ""))
                html_string += "</tr>"

                for row in cve_table:
                    # Check if the row contains an element with the key "is_exploit"
                    is_exploit = False
                    exploit_available = False
                    for elem in row["elem"]:
                        if elem["@key"] == "id":
                            exploit_available = (
                                "EDB" in elem["#text"] or "CVE" in elem["#text"]
                            ) and "MSF" not in elem["#text"]
                        if elem["@key"] == "is_exploit":
                            is_exploit = elem["#text"] == "true"

                    # Construct the opening tag for the table row
                    if is_exploit:
                        if exploit_available:
                            html_string += "<tr class='exploit_available'>"
                        else:
                            html_string += "<tr class='exploit_less_details'>"
                    else:
                        html_string += "<tr>"

                    # Construct table cells for each element in the row
                    for elem in row["elem"]:
                        if elem["@key"] == "id":
                            html_string += "<td class='vuln_code'>{}</td>".format(
                                elem["#text"]
                            )
                        elif elem["@key"] == "type":
                            html_string += "<td class='vuln_type'>{}</td>".format(
                                elem["#text"]
                            )
                        else:
                            html_string += "<td>{}</td>".format(elem["#text"])

                    # Close the table row
                    html_string += "</tr>"

                html_string += "</table><br><br>"

        return html_string
